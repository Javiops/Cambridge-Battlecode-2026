"""Extract current-only solo controller dispatch and the common consumer.

The World/input records are explicit model fixtures. This is not native current
quote, visibility, route, cost or execution evidence.
"""
from pathlib import Path
import hashlib
import json
import re


def _function(text, name):
    match = re.search(r"\binline\s+[^{};]*\b" + name + r"\s*\(", text)
    if not match:
        raise ValueError("Missing production solo controller function: " + name)
    start = match.start()
    end = text.index("{", match.end()) + 1
    depth = 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def _parts(source):
    source = Path(source)
    solo = (source / "solo.h").read_text(encoding="utf8")
    economy = (source / "economy.h").read_text(encoding="utf8")
    current = _function(solo, "quote_current_solo_clear")
    cast = _function(solo, "quote_solo_cast_farm")
    full = _function(solo, "quote_solo_farm")
    compact = lambda value: re.sub(r"\s+", "", value)
    if "if(autodispatched=current_solo_dispatch(w,gi))return*dispatched;" not in compact(current):
        raise ValueError("Current-only quote must dispatch the committed controller first")
    if "current_only?w.memory.mission.solo_slot:-1" not in compact(cast):
        raise ValueError("Current direct certificate must receive its actual committed slot")
    if "current_solo_mode(w.memory.mission,gi)==SoloFarmMode::DirectCastOnly" not in compact(full):
        raise ValueError("Full quote's incumbent-outer priority must require explicit Direct mode")
    return {
        "EXACT_CURRENT_DISPATCH": _function(solo, "current_solo_dispatch"),
        "EXACT_TYPED_SOLO_CONSUMER": _function(economy, "solo_farm_proposal"),
        "BIND_CURRENT_CALLER": current,
        "BIND_CAST_SLOT_ADAPTER": cast,
        "BIND_FULL_QUOTE": full,
    }


def extract_solo_mode(source):
    return "\n".join(_parts(source).values())


def generate_solo_mode_fixture(source, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    parts = _parts(source)
    text = (Path(__file__).parent / "fixtures/solo-mode.cpp").read_text(encoding="utf8")
    for name in ("EXACT_CURRENT_DISPATCH", "EXACT_TYPED_SOLO_CONSUMER"):
        marker = "// " + name
        if text.count(marker) != 1:
            raise ValueError("Missing/duplicate solo mode marker: " + name)
        text = text.replace(marker, parts[name])
    target = output / "solo-mode-generated.cpp"
    target.write_text(text, encoding="utf8")
    (output / "solo-mode-extracted.json").write_text(json.dumps({
        name: hashlib.sha256(value.encode()).hexdigest() for name, value in parts.items()
    }, indent=2) + "\n", encoding="utf8")
    return target
