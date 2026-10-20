"""Batched actor-turn access to the pinned official rules module (not a rewritten simulator)."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json
from pathlib import Path
import subprocess
import uuid

from . import core, mapgen


class Environment:
    def __init__(self):
        executable, engine = mapgen.node(), mapgen.engine_path()
        self.reader = ThreadPoolExecutor(1)
        self.sequence = 0
        self.log = core.ROOT / ".cambc" / ("engine-" + uuid.uuid4().hex + ".stderr")
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.stderr = self.log.open("w", encoding="utf-8")
        try:
            self.process = subprocess.Popen([executable, "--no-warnings", str(core.ROOT / "lab/engine.mjs"),
                                             str(engine), "serve"], stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE, stderr=self.stderr, text=True,
                                            encoding="utf-8", cwd=core.ROOT, env=core.ENV, bufsize=1)
        except OSError:
            self.stderr.close()
            self.reader.shutdown(wait=False)
            raise

    def request(self, **command):
        self._validate_maps(command)
        self.sequence += 1
        command["id"] = self.sequence
        self.process.stdin.write(json.dumps(command, allow_nan=False) + "\n")
        self.process.stdin.flush()
        future = self.reader.submit(self.process.stdout.readline)
        try:
            line = future.result(timeout=core.config()["stage1"].get("request_timeout", 30))
        except TimeoutError:
            self.process.kill()
            raise RuntimeError("Official engine bridge timed out; episode is invalid") from None
        if not line:
            self.stderr.flush()
            raise RuntimeError("Official engine bridge exited: " + self.log.read_text()[-1500:])
        result = json.loads(line)
        if result.get("id") != self.sequence:
            raise RuntimeError("Mismatched official engine response")
        if not result.get("ok"):
            raise ValueError(result.get("error", "Engine request failed"))
        return result["result"]

    @staticmethod
    def _validate_maps(command):
        if command.get("op") == "batch":
            for child in command.get("commands", []):
                Environment._validate_maps(child)
        if command.get("op") == "reset":
            path = Path(command["map"]).resolve()
            root = core.MAPS.resolve()
            sealed = {(root/(name+".map26a")).resolve() for name in core.config()["maps"]["confirm"]}
            if not path.is_relative_to(root) or path in sealed or "confirm" in path.relative_to(root).parts:
                raise ValueError("Confirmation maps are sealed from training environments")

    def batch_steps(self, transitions):
        """One response per (episode id, current actor, action), with isolated item errors."""
        return self.request(op="batch", commands=[dict(op="step", env_id=e, actor=a, action=c)
                                                  for e, a, c in transitions])

    def reset(self, map_name: str, picks=None):
        if map_name in core.config()["maps"]["confirm"] or "/confirm/" in map_name:
            raise ValueError("Confirmation maps are sealed from training environments")
        command = {"op": "reset", "map": str(core.map_path(map_name))}
        if picks is not None:
            command["picks"] = picks
        result = self.request(**command)
        expected = core.config()["stage1"]["engine_wasm_sha256"]
        if result["engine_sha256"] != expected:
            raise RuntimeError("Wrong official rules module")
        return result

    def step(self, env_id, actor, action, *, observe=True):
        return self.request(op="step", env_id=env_id, actor=actor, action=action, observe=observe)

    def close_episode(self, env_id):
        return self.request(op="close", env_id=env_id)

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self.reader.shutdown(wait=True, cancel_futures=True)
        self.stderr.close()
        self.process.stdout.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
