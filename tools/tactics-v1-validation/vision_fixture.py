"""Generate a small World adapter around exact production ward functions."""
from pathlib import Path


def extract_vision_policy(source):
    text = (Path(source) / "vision.h").read_text(encoding="utf8")

    def extract(name):
        location = text.index(name)
        start = text.rfind("inline ", 0, location)
        opening = text.index("{", location)
        depth, i = 1, opening + 1
        while depth:
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        return text[start:i]

    return "\n".join(extract(name) for name in
                     ("ward_blocked_phase", "ward_local_bit", "ward_opportunity", "ward_buffer_score"))


def generate_vision_fixture(source, output):
    template = Path(__file__).parent / "fixtures" / "vision.cpp"
    destination = Path(output) / "vision.generated.cpp"
    destination.write_text(template.read_text(encoding="utf8").replace(
        "// EXACT_PRODUCTION_FUNCTIONS", extract_vision_policy(source)), encoding="utf8")
    return destination
