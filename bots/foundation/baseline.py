"""Verify the frozen legacy sources; never infer which bot is live."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).with_name('baseline.json')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_identity(directory):
    directory = Path(directory)
    files = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlink in source tree: {path}')
        if path.is_file():
            files[path.relative_to(directory).as_posix()] = sha(path)
    if not files:
        raise ValueError(f'Missing or empty source tree: {directory}')
    encoded = json.dumps(files, sort_keys=True, separators=(',', ':')).encode()
    return {'sha256': hashlib.sha256(encoded).hexdigest(), 'files': files}


def verify(root=ROOT, manifest=None):
    data = json.loads(MANIFEST.read_text(encoding='utf-8')) if manifest is None else manifest
    if data.get('schema') != 1 or not data.get('protected_bots'):
        raise ValueError('Missing baseline schema or protected bots')
    for name, expected in data['protected_bots'].items():
        if not name or Path(name).name != name or name in ('.', '..', 'foundation'):
            raise ValueError('Invalid protected bot name')
        if source_identity(Path(root) / 'bots' / name / 'src') != expected:
            raise ValueError(f'Protected source changed: bots/{name}/src')
    return data


if __name__ == '__main__':
    data = verify()
    print(f"PASS: {len(data['protected_bots'])} legacy bot source trees match {data['source_commit']}")
    print('Live upload identity: unverified; use online/version.py with the exact uploaded ZIP.')
