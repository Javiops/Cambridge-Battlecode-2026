"""Extract the exact observation wrapper; SDK/cache/budget inputs are explicit stand-ins."""
from pathlib import Path
import re

def extract_observation_detour(source):
    text=(Path(source)/'economy.h').read_text(encoding='utf8')
    match=re.search(r'inline\s+std::optional<Pos>\s+safe_observation_detour\s*\(',text)
    if not match:raise ValueError('Missing safe_observation_detour')
    opening=text.index('{',match.end());end=opening+1;depth=1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[match.start():end]

def generate_observation_detour_fixture(source,output):
    here=Path(__file__).resolve().parent
    template=here/'fixtures/observation-detour-caller.cpp'
    if not template.is_file():template=here/'detour-caller.cpp'
    out=Path(output)/'observation-detour-caller.generated.cpp'
    out.write_text(template.read_text(encoding='utf8').replace('/*EXACT_OBSERVATION_DETOUR*/',extract_observation_detour(source)),encoding='utf8')
    return out
