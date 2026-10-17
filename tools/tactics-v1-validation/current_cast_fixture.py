"""Source-extracted current-cast admission, funding and proof-carry checks.

Inputs and model outcomes in the fixtures are explicit projections. Actual
native selector/controller/action evidence is retained in the separate probe.
"""
from pathlib import Path
import hashlib
import json
import re


def _function(text, name, structure=False):
    pattern = ((r"struct\s+" if structure else r"inline\s+(?:bool|std::optional<Proposal>)\s+")
               + name + r"\b")
    match = re.search(pattern, text)
    if not match:
        raise ValueError("Missing production declaration: " + name)
    start = match.start()
    end = text.index("{", start) + 1
    depth = 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    if structure:
        end = text.index(";", end) + 1
    return text[start:end]


def extract_cast_admission(source):
    text = (Path(source) / "economy.h").read_text(encoding="utf8")
    function = _function(text, "current_camp_assignment_candidate")
    if text.count("current_camp_assignment_candidate(") != 2:
        raise ValueError("Ordinary farming must use the reviewed admission helper")
    return function


def _current_parts(source):
    source = Path(source)
    economy = (source / "economy.h").read_text(encoding="utf8")
    coordination = (source / "coordination.h").read_text(encoding="utf8")
    main = (source / "main.cpp").read_text(encoding="utf8")
    if not re.search(r"AssignmentFunding\s+funding\s*=\s*AssignmentFunding::Ordinary", coordination):
        raise ValueError("Generic assignment funding must default to Ordinary")
    match = re.search(r"inline\s+LocalAssignment\s+propose_local_assignment\s*\(", coordination)
    if not match:
        raise ValueError("Missing production assignment controller")
    declaration = match.start()
    if not re.search(r"bc::fuel_remaining\(\)\s*<\s*48000", coordination[declaration:declaration+500]):
        raise ValueError("Actual assignment entry admission must remain48k")
    funding_start = coordination.index("enum class AssignmentFunding ")
    funding = coordination[funding_start:declaration]
    compact = re.sub(r"\s+", "", economy)
    for required in (
        "if(current_cast&&!current_cast_quote_valid(w,m,*current_cast))",
        "prepaid_assignment=std::move(current_cast->assignment)",
        "current_cast->serial=-1;",
    ):
        if required not in compact:
            raise ValueError("Missing current-snapshot proof consumer: " + required)
    hook = re.search(r"early_current_cast_farm_proposal\s*\(\s*w,\s*memory_,\s*transaction\s*\|\|\s*chain_\.active\(\)\s*\|\|\s*awake_entry_active\(memory_\.awake_entry\)\s*\)", main)
    if (not hook or hook.start() < main.index("early_solo_proposal(")
            or hook.start() > main.index("early_assembly_eligible(")):
        raise ValueError("Current-cast hook must preserve prior early SOLO and precede early assembly")
    return {
        "EXACT_FUNDING": funding,
        "EXACT_TYPES": _function(economy, "FarmCandidate", True) + "\n" + _function(economy, "CurrentCastFarmQuote", True),
        "EXACT_VALIDITY": _function(economy, "current_cast_quote_valid"),
        "EXACT_EARLY": _function(economy, "early_current_cast_farm_proposal"),
    }


def extract_current_cast(source):
    return "\n".join(_current_parts(source).values())


def _generate(source, output, name, replacements):
    source, output = Path(source), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    template = Path(__file__).parent / "fixtures" / (name + ".cpp")
    text = template.read_text(encoding="utf8")
    for marker, value in replacements.items():
        if text.count("// " + marker) != 1:
            raise ValueError("Missing unique fixture insertion: " + marker)
        text = text.replace("// " + marker, value)
    path = output / (name + ".generated.cpp")
    path.write_text(text, encoding="utf8")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    binding = {
        "source_sha256": {name: sha(source / name) for name in ("economy.h", "coordination.h", "main.cpp")},
        "extracted_sha256": hashlib.sha256("\n".join(replacements.values()).encode()).hexdigest(),
        "fixture_sha256": sha(path),
        "scope": "Exact production declarations and caller/floor assertions; explicit World/model inputs, not native gameplay reconstruction.",
    }
    (output / (name + "-binding.json")).write_text(json.dumps(binding, indent=2) + "\n", encoding="utf8")
    return path


def generate_cast_admission_fixture(source, output):
    return _generate(source, output, "cast-admission", {"EXACT_ADMISSION": extract_cast_admission(source)})


def generate_current_cast_fixture(source, output):
    return _generate(source, output, "current-cast", _current_parts(source))
