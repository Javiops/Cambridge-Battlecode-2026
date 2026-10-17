"""Extract the production bounded separate-opportunity scan without SDK calls."""
from pathlib import Path


def extract_alternative(source):
    text = (Path(source) / "coordination.h").read_text(encoding="utf8")
    start = text.index("inline double alternative(")
    opening = text.index("{", start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def generate_alternative_fixture(source, output):
    template = Path(__file__).parent / "fixtures" / "alternative.cpp"
    destination = Path(output) / "alternative.generated.cpp"
    destination.write_text(template.read_text(encoding="utf8").replace(
        "// EXACT_ALTERNATIVE", extract_alternative(source)), encoding="utf8")
    return destination
