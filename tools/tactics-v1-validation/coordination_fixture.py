"""Extract exact current cached-geometry formation proposal for local fixtures."""
from pathlib import Path


def extract_squad_position(source):
    text = (Path(source) / "coordination.h").read_text(encoding="utf8")
    start = text.index("inline std::optional<Pos> squad_position(")
    opening = text.index("{", start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def generate_squad_position_fixture(source, output):
    template = Path(__file__).parent / "fixtures" / "squad-position.cpp"
    destination = Path(output) / "squad-position.generated.cpp"
    destination.write_text(template.read_text(encoding="utf8").replace(
        "// EXACT_SQUAD_POSITION", extract_squad_position(source)), encoding="utf8")
    return destination
