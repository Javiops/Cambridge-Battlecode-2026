from pathlib import Path
def extract_pending_awake(source):
 text=(Path(source)/'economy.h').read_text();start=text.index('inline std::optional<Proposal> pending_awake_entry_proposal(');i=text.index('{',start)+1;depth=1
 while depth:
  if text[i]=='{':depth+=1
  if text[i]=='}':depth-=1
  i+=1
 return text[start:i]
def generate_pending_awake_fixture(source,output):
 here=Path(__file__).resolve().parent
 template=here/'fixtures/awake-entry-caller.cpp'
 if not template.exists():template=here/'pending-caller-template.cpp'
 text=template.read_text().replace('/*PRODUCTION_PENDING_CURRENT*/',extract_pending_awake(source))
 out=Path(output)/'awake-entry-caller.cpp';out.write_text(text);return out
