"""Extract the exact production rendezvous admission/control-flow wrapper.

The fixture stubs the expensive quote and SDK; native route/readiness and the
production main are covered by separate native tests, never by these stubs.
"""
from pathlib import Path
import re


def extract_handshake(source):
    text = (Path(source) / 'coordinator.h').read_text(encoding='utf8')
    declaration = re.search(
        r'inline\s+std::optional\s*<\s*Proposal\s*>\s+'
        r'assembly_handshake_proposal\s*\(', text)
    if declaration is None:
        raise ValueError('Cannot find the assembly_handshake_proposal definition')
    start = declaration.start()
    opening = text.index('{', start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


def generate_handshake_fixture(source, output):
    template = Path(__file__).parent / 'fixtures/assembly-handshake.cpp'
    fixture = Path(output) / 'assembly-handshake.generated.cpp'
    fixture.write_text(template.read_text(encoding='utf8').replace(
        '// EXACT_HANDSHAKE', extract_handshake(source)), encoding='utf8')
    return fixture
