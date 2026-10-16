from pathlib import Path
HERE=Path(__file__).resolve().parent
def extract_solo_basic_policy(source):
 text=(Path(source)/"economy.h").read_text(encoding="utf8")
 economic=text[text.index("inline Proposal economic("):text.index("inline Action moving(")]
 receipt=text[text.index("inline SoloBasicReceipt make_solo_basic_receipt("):text.index("inline SoloResetReceipt make_solo_reset_receipt(")]
 return economic+receipt
def generate_solo_basic_fixture(source,output):
 path=Path(output)/"solo-basic.generated.cpp"
 template=(HERE/"fixtures/solo-basic.cpp").read_text(encoding="utf8")
 path.write_text(template.replace("// PRODUCTION_SOLO_BASIC",extract_solo_basic_policy(source)),encoding="utf8")
 return path
