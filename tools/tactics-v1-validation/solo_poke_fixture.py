"""Exact typed solo proposal consumer against small explicit model snapshots."""
from pathlib import Path

def extract_solo_poke_consumer(source):
    text=(Path(source)/'economy.h').read_text(encoding='utf8')
    start=text.index('inline std::optional<Proposal> solo_farm_proposal(')
    opening=text.index('{',start);end=opening+1;depth=1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]

def generate_solo_poke_consumer(source,output):
    out=Path(output)/'solo-poke-consumer.generated.cpp'
    template=(Path(__file__).parent/'fixtures/solo-poke-consumer.cpp').read_text(encoding='utf8')
    out.write_text(template.replace('// EXACT_TYPED_SOLO_CONSUMER',extract_solo_poke_consumer(source)),encoding='utf8')
    return out
