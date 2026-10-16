"""Extract the production cached contribution-arrival policy into narrow inputs."""
from pathlib import Path
import re

def _block(text, token, semicolon=False):
    start = text.index(token)
    opening = text.index('{', start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end] + (';' if semicolon else '')

def extract_assembly_arrival(source):
    text = (Path(source) / 'assembly.h').read_text(encoding='utf8')
    start = text.index('inline Arrival contribution_arrival(')
    opening = start + re.search(r'\)\s*\{',text[start:]).end() - 1
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

def extract_assembly_policy(source):
    text = (Path(source) / 'assembly.h').read_text(encoding='utf8')
    return '\n'.join((_block(text, 'struct Arrival {', True),
        _block(text, 'inline bool basic_coverage(') if 'inline bool basic_coverage(' in text else '',
        extract_assembly_arrival(source),_block(text,'inline std::optional<Pos> assembly_step('),
        _block(text,'inline std::uint64_t fingerprint(')))

def generate_assembly_arrival_fixture(source, output):
    template = Path(__file__).parent / 'fixtures/assembly-arrival.cpp'
    fixture = Path(output) / 'assembly-arrival.generated.cpp'
    text = (Path(source) / 'assembly.h').read_text(encoding='utf8')
    fixture.write_text(template.read_text(encoding='utf8').replace(
        '// EXACT_ASSEMBLY_ARRIVAL_TYPE', _block(text,'struct Arrival {',True)+'\n'+
        (_block(text,'inline bool basic_coverage(') if 'inline bool basic_coverage(' in text else '')).replace(
        '// EXACT_ASSEMBLY_ARRIVAL', extract_assembly_arrival(source)).replace(
        '// EXACT_ASSEMBLY_FINGERPRINT', _block(text,'inline std::uint64_t fingerprint(')).replace(
        '// EXACT_ASSEMBLY_STEP', _block(text,'inline std::optional<Pos> assembly_step(')), encoding='utf8')
    return fixture
