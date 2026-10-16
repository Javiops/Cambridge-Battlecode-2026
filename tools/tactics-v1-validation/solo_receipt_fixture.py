from pathlib import Path
HERE=Path(__file__).resolve().parent

def extract_solo_receipt_policy(source):
    text=(Path(source)/"economy.h").read_text(encoding="utf8")
    economic=text[text.index("inline Proposal economic("):text.index("inline Action moving(")]
    receipt=text[text.index("inline SoloResetReceipt make_solo_reset_receipt("):text.index("inline std::optional<Proposal> farming(")]
    return economic+receipt

def generate_solo_receipt_fixture(source,output):
    path=Path(output)/"solo-receipt.generated.cpp"
    template=(HERE/"fixtures/solo-receipt.cpp").read_text(encoding="utf8")
    assert "// PRODUCTION_SOLO_RECEIPT" in template
    path.write_text(template.replace("// PRODUCTION_SOLO_RECEIPT",extract_solo_receipt_policy(source)),encoding="utf8")
    return path
