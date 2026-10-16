"""Build a fixture around the exact production channel risk function.

Only public reach-set/World inputs are replaced by deterministic fixtures;
the channel policy itself and SDK-free combat helpers are production code.
Native geometry, actions and engine timing need separate integration evidence.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = "// INSERT_PRODUCTION_CHANNEL_FUNCTION"


def extract_channel_function(source: Path) -> str:
    text = (Path(source) / "economy.h").read_text(encoding="utf8")
    start = text.index("inline bool channel_interruption_risk(")
    brace = text.index("{", start)
    depth, end = 1, brace + 1
    while depth:
        if end >= len(text):
            raise ValueError("Unterminated production channel risk function")
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def generate_channel_fixture(source: Path, output: Path) -> Path:
    template = (HERE / "fixtures/channel.cpp").read_text(encoding="utf8")
    if template.count(MARKER) != 1:
        raise ValueError("Channel fixture must contain exactly one production insertion marker")
    target = Path(output) / "channel.generated.cpp"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template.replace(MARKER, extract_channel_function(source)), encoding="utf8")
    return target


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(generate_channel_fixture(args.source, args.output))
