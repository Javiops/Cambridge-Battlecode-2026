"""Regression: formatter line breaks do not change the extracted policy/test."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
from handshake_fixture import extract_handshake, generate_handshake_fixture
from run_tests import compiler_path, find_tool


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--compiler', type=Path)
    parser.add_argument('--node', type=Path)
    a = parser.parse_args()
    source, output = a.source.resolve(), a.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    original = extract_handshake(source)
    canonical = re.sub(r'\s+', ' ', original).strip()
    declaration = r'inline\s+std::optional\s*<\s*Proposal\s*>\s+assembly_handshake_proposal\s*\('
    layouts = {
        'single-line': 'inline std::optional<Proposal> assembly_handshake_proposal(',
        'formatted': 'inline std::optional<Proposal>\nassembly_handshake_proposal(',
    }
    compiler = compiler_path(a.compiler)
    node = find_tool(a.node, 'NODE', 'node')
    results = []
    for label, replacement in layouts.items():
        directory = output / label
        directory.mkdir(exist_ok=True)
        header = directory / 'coordinator.h'
        header.write_text(re.sub(declaration, replacement, original, count=1), encoding='utf8')
        extracted = extract_handshake(directory)
        if re.sub(r'\s+', ' ', extracted).strip() != canonical:
            raise AssertionError('Formatting changed extracted tokens: ' + label)
        fixture = generate_handshake_fixture(directory, directory)
        wasm = directory / 'fixture.wasm'
        commands = (
            [compiler, '-std=c++20', '-O1', '-fwasm-exceptions', '-mllvm',
             '-wasm-use-legacy-eh=false', '-I', source, fixture, '-lunwind', '-o', wasm],
            [node, Path(__file__).parent / 'run-wasi.mjs', wasm],
        )
        for phase, command in zip(('compile', 'run'), commands):
            r = subprocess.run(list(map(str, command)), text=True, capture_output=True,
                               errors='replace', timeout=120)
            (directory / (phase + '.stdout.txt')).write_text(r.stdout, encoding='utf8')
            (directory / (phase + '.stderr.txt')).write_text(r.stderr, encoding='utf8')
            if r.returncode:
                raise AssertionError(label + ':' + phase + '\n' + r.stdout + r.stderr)
        if '36 assembly handshake checks passed' not in r.stdout:
            raise AssertionError('Missing semantic-check marker: ' + label)
        results.append({'layout': label, 'passed': True, 'stdout': r.stdout.strip(),
                        'fixture_sha256': sha(fixture), 'wasm_sha256': sha(wasm)})
    absent = output / 'absent'
    absent.mkdir(exist_ok=True)
    (absent / 'coordinator.h').write_text('inline void other() {}\n', encoding='utf8')
    try:
        extract_handshake(absent)
        raise AssertionError('Missing declaration should fail explicitly')
    except ValueError:
        pass
    report = {'passed': True, 'semantic_checks_per_layout': 36,
              'canonical_function_sha256': hashlib.sha256(canonical.encode()).hexdigest(),
              'generator_sha256': sha(Path(__file__).parent / 'handshake_fixture.py'),
              'source_coordinator_sha256': sha(source / 'coordinator.h'), 'cases': results,
              'missing_declaration_rejected': True,
              'scope': 'Actual extracted policy tokens and semantic fixtures; no native gameplay claim.'}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
