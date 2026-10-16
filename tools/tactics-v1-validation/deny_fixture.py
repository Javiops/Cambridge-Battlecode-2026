"""Extract current denial wrapper around exact SDK-free production helpers."""
from pathlib import Path


def extract_denial_proposal(source):
    text = (Path(source) / "deny.h").read_text(encoding="utf8")
    start = text.index("inline std::optional<Proposal> denial_proposal(")
    opening = text.index("{", start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def generate_denial_fixture(source, output):
    template = Path(__file__).parent / "fixtures" / "deny.cpp"
    destination = Path(output) / "deny.generated.cpp"
    destination.write_text(template.read_text(encoding="utf8").replace(
        "// EXACT_DENIAL_PROPOSAL", extract_denial_proposal(source)), encoding="utf8")
    return destination
