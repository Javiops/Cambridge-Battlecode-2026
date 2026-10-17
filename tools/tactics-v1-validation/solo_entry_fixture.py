"""Exact early-solo eligibility plus bounded personal route helpers."""
from pathlib import Path
import re

def extract_solo_entry(source):
    text=(Path(source)/'economy.h').read_text(encoding='utf8')
    functions=[]
    for name in ('early_solo_eligible','early_solo_proposal'):
        m=re.search(r'inline\s+(?:bool|std::optional<Proposal>)\s+'+name+r'\s*\(',text)
        if not m:raise ValueError('Missing '+name)
        start=m.start();opening=text.index('{',start);end=opening+1;depth=1
        while depth:
            depth+=(text[end]=='{')-(text[end]=='}');end+=1
        functions.append(text[start:end])
    return '\n\n'.join(functions)

def generate_solo_entry_fixture(source,output):
    out=Path(output)/'solo-entry.generated.cpp'
    out.write_text((Path(__file__).parent/'fixtures/solo-entry.cpp').read_text(encoding='utf8').replace('// EXACT_SOLO_ENTRY',extract_solo_entry(source)),encoding='utf8')
    return out
