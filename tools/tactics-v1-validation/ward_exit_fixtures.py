"""Generate ward/exit tests from exact production helpers, without SDK stubs.

The template retains the pre-optimization ranking as a reference. Production
exit semantics are included directly under their SDK-free model boundary.
"""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
MARKER = "// INSERT_PRODUCTION_WARD_HELPERS"
HELPERS = (
    "struct WardScoreByte",
    "inline unsigned ward_interval_bits(",
    "inline std::vector<WardScoreByte> ward_score_stencil(",
    "inline int ward_stencil_score(",
    "inline bool ward_local_bit(",
    "inline int ward_buffer_score(",
    "inline std::vector<Pos> ward_candidate_positions(",
)


def _extract(text: str, marker: str) -> str:
    if text.count(marker) != 1:
        raise ValueError(f"Expected exactly one production ward helper: {marker}")
    start = text.index(marker)
    brace = text.index("{", start)
    end, depth = brace + 1, 1
    while depth:
        if end >= len(text):
            raise ValueError(f"Unterminated production ward helper: {marker}")
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    if text[end:end + 1] == ";":
        end += 1
    return text[start:end]


def extract_ward_exit_policy(source: Path) -> str:
    source = Path(source)
    vision = (source / "vision.h").read_text(encoding="utf8")
    strategic = (source / "strategic.h").read_text(encoding="utf8")
    return strategic + "\n" + "\n".join(_extract(vision, marker) for marker in HELPERS)


def generate_ward_exit_fixture(source: Path, output: Path) -> Path:
    source, output = Path(source), Path(output)
    names = ("types.h", "vision.h", "strategic.h")
    before = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in names}
    template = (HERE / "fixtures/ward-exit.cpp").read_text(encoding="utf8")
    if template.count(MARKER) != 1:
        raise ValueError("Ward/exit fixture requires exactly one production insertion marker")
    vision = (source / "vision.h").read_text(encoding="utf8")
    helpers = "namespace tactics {\n" + "\n".join(_extract(vision, m) for m in HELPERS) + "\n}"
    generated = template.replace(MARKER, helpers)
    after = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in names}
    if before != after:
        raise RuntimeError("Production ward/exit inputs changed during extraction")
    output.mkdir(parents=True, exist_ok=True)
    target = output / "ward-exit.generated.cpp"
    target.write_text(generated, encoding="utf8")
    manifest = {
        "source_sha256": before,
        "template_sha256": hashlib.sha256(template.encode()).hexdigest(),
        "generated_sha256": hashlib.sha256(generated.encode()).hexdigest(),
        "production_function_sha256": hashlib.sha256(extract_ward_exit_policy(source).encode()).hexdigest(),
        "scope": "1,600 packed-score equivalence cases, 1,600 anchor-ranking equivalence cases including blocked desired anchors, and eight exit timing/uncertainty scenarios. Native masks, placement and fuel require separate validation.",
    }
    (output / "ward-exit.source.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8")
    return target


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(generate_ward_exit_fixture(args.source, args.output))
