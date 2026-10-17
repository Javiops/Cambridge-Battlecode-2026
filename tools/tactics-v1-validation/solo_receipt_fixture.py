from pathlib import Path
import re
HERE=Path(__file__).resolve().parent

def _function(text, signature):
    """Extract exactly one balanced function, skipping comments/string braces."""
    match = re.search(signature, text)
    if not match:
        raise ValueError("Missing production function: " + signature)
    start = match.start()
    opening = text.index("{", start)
    depth = 0
    tokens = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}]', re.S)
    for token in tokens.finditer(text, opening):
        if token.group() == "{":
            depth += 1
        elif token.group() == "}":
            depth -= 1
            if depth == 0:
                return text[start:token.end()] + "\n"
    raise ValueError("Unclosed production function: " + signature)

def extract_solo_receipt_policy(source):
    text=(Path(source)/"economy.h").read_text(encoding="utf8")
    return (_function(text, r"inline\s+Proposal\s+economic\s*\(") +
            _function(text, r"inline\s+SoloResetReceipt\s+make_solo_reset_receipt\s*\(") +
            _function(text, r"inline\s+std::optional<Proposal>\s+solo_reset_basic_followup\s*\("))

def generate_solo_receipt_fixture(source,output):
    path=Path(output)/"solo-receipt.generated.cpp"
    template=(HERE/"fixtures/solo-receipt.cpp").read_text(encoding="utf8")
    assert "// PRODUCTION_SOLO_RECEIPT" in template
    path.write_text(template.replace("// PRODUCTION_SOLO_RECEIPT",extract_solo_receipt_policy(source)),encoding="utf8")
    return path
