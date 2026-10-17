"""Exact production coarse-fallback certificate/provenance with explicit inputs."""
from pathlib import Path
import hashlib,json,re

def extract_coarse_fallback(source):
    text=(Path(source)/'economy.h').read_text(encoding='utf8')
    functions=[]
    for name in ('current_basic_farm_fallback','use_basic_farm_fallback'):
        match=re.search(r'inline\s+(?:CampRollout|void)\s+'+name+r'\s*\(',text)
        if not match:raise ValueError('Missing '+name)
        start=match.start();end=text.index('{',start)+1;depth=1
        while depth:
            depth+=(text[end]=='{')-(text[end]=='}');end+=1
        functions.append(text[start:end])
    # Bind the two authorization sites too: a passing helper must not coexist
    # with the old unfunded heuristic caller in the tested source snapshot.
    if not re.search(r'bool\s+ready\s*=\s*hp\s*<=\s*0\s*\|\|\s*out\.basic_fallback\.ready',text):
        raise ValueError('evaluate_farm readiness is not certificate-gated')
    if not re.search(r'!assignment\.ready\s*&&\s*assignment\.uncertain\s*&&\s*conservative_ready',text):
        raise ValueError('Unknown assignment does not use reviewed proof fallback')
    if not re.search(r'best\.ready\s*&&\s*!assignment\.ready\s*&&\s*best\.basic_fallback\.ready',text):
        raise ValueError('Skipped assignment does not carry reviewed proof provenance')
    return '\n'.join(functions)

def generate_coarse_fallback_fixture(source,output):
    text=(Path(source)/'economy.h').read_text(encoding='utf8')
    functions=extract_coarse_fallback(source)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    path=output/'coarse-fallback.generated.cpp'
    fixture=(Path(__file__).parent/'fixtures/coarse-fallback.cpp').read_text(encoding='utf8')
    path.write_text(fixture.replace('// EXACT_FALLBACK',functions),encoding='utf8')
    binding={'economy_sha256':hashlib.sha256(text.encode()).hexdigest(),
             'extracted_functions_sha256':hashlib.sha256(functions.encode()).hexdigest(),
             'fixture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
             'scope':'Exact production helper/provenance, explicit World fixture inputs; not a native gameplay or performance reconstruction.'}
    (output/'coarse-fallback-binding.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf8')
    return path
