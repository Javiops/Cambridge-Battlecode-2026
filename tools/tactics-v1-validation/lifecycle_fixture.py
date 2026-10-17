"""Exact new-owner intent maintenance; SDK/world queries are narrow test stand-ins."""
from pathlib import Path
import re

def extract_assembly_lifecycle(source):
    text=(Path(source)/'coordinator.h').read_text(encoding='utf8')
    functions=[]
    for name in ('observe_hold','release_stalled_unnamed_assembly','observe_progress'):
        m=re.search(r'inline\s+(?:void|bool)\s+'+name+r'\s*\(',text)
        if m is None: raise ValueError('Missing lifecycle function '+name)
        start=m.start();opening=text.index('{',m.end());depth=1;end=opening+1
        while depth:
            depth+=(text[end]=='{')-(text[end]=='}');end+=1
        functions.append(text[start:end])
    return '\n'.join(functions)

def extract_prepare_route(source):
    text=(Path(source)/'main.cpp').read_text(encoding='utf8')
    m=re.search(r'void\s+prepare_route\s*\(',text)
    if m is None: raise ValueError('Missing prepare_route')
    start=m.start();opening=text.index('{',m.end());depth=1;end=opening+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]

def generate_assembly_lifecycle(source,output):
    path=Path(output)/'assembly-lifecycle.generated.cpp'
    template=Path(__file__).parent/'fixtures/assembly-lifecycle.cpp'
    path.write_text(template.read_text(encoding='utf8').replace('// EXACT_LIFECYCLE',extract_assembly_lifecycle(source)).replace('// EXACT_PREPARE_ROUTE',extract_prepare_route(source)),encoding='utf8')
    return path
