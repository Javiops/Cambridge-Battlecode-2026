from pathlib import Path
HERE=Path(__file__).resolve().parent
def extract_solo_basic_policy(source):
 text=(Path(source)/"economy.h").read_text(encoding="utf8")
 economic=text[text.index("inline Proposal economic("):text.index("inline Action moving(")]
 receipt=text[text.index("inline SoloBasicReceipt make_solo_basic_receipt("):text.index("inline SoloResetReceipt make_solo_reset_receipt(")]
 solo=(Path(source)/"solo.h").read_text(encoding="utf8")
 lethal=""
 if "inline bool solo_guaranteed_current_basic_kill(" in solo:
  start=solo.index("inline bool solo_guaranteed_current_basic_kill(")
  end=solo.index("// Re-certify one already committed",start)
  lethal="\n#define TACTICS_SOLO_LETHAL_BOUND\n"+solo[start:end]
 return economic+receipt+lethal
def generate_solo_basic_fixture(source,output):
 path=Path(output)/"solo-basic.generated.cpp"
 # Preserve historical frozen sources: only explicit paid owner-provenance
 # headers use the typed sequence fixture; old reset-only contract is retained.
 typed="solo_current_followup" in (Path(source)/"types.h").read_text(encoding="utf8")
 template=(HERE/"fixtures"/("solo-sequence.cpp" if typed else "solo-basic.cpp")).read_text(encoding="utf8")
 path.write_text(template.replace("// PRODUCTION_SOLO_BASIC",extract_solo_basic_policy(source)),encoding="utf8")
 return path
