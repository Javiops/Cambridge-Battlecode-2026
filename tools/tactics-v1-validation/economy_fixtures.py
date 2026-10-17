"""Generate focused fixtures from the exact production economy policies.

World walking, safety and visibility inputs are fixture data. These checks do
not replace native pathfinding, action legality or full game timing evidence.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent


def extract_economy_policy(name: str, source: Path) -> str:
    text = (Path(source) / "economy.h").read_text(encoding="utf8")
    if name == "delivery":
        return text[text.index("struct AltarPlan {"):text.index("inline bool needs_recovery(")]
    if name != "recovery":
        raise ValueError("Economy fixture must be recovery or delivery")
    start = text.index("inline std::optional<Proposal> recovery(")
    brace = text.index("{", start)
    depth, end = 1, brace + 1
    while depth:
        if end >= len(text):
            raise ValueError("Unterminated production recovery function")
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def generate_economy_fixture(name: str, source: Path, output: Path) -> Path:
    markers = {
        "recovery": "// INSERT_PRODUCTION_RECOVERY_FUNCTION",
        "delivery": "// INSERT_PRODUCTION_ALTAR_AND_DELIVERY",
    }
    if name not in markers:
        raise ValueError("Economy fixture must be recovery or delivery")
    template = (HERE / "fixtures" / f"{name}.cpp").read_text(encoding="utf8")
    marker = markers[name]
    if template.count(marker) != 1:
        raise ValueError("Expected exactly one production insertion marker")
    target = Path(output) / f"{name}.generated.cpp"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template.replace(marker, extract_economy_policy(name, source)), encoding="utf8")
    return target


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", choices=["recovery", "delivery"])
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(generate_economy_fixture(args.name, args.source, args.output))
