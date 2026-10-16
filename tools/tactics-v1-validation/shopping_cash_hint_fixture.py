"""Exact producer-to-consumer cash route hint with cache/World stand-ins."""
from pathlib import Path

def extract_shopping_cash_hint(source):
    text=(Path(source)/"shopping.h").read_text(encoding="utf8")
    start=text.index("inline std::optional<Pos> shopping_gem_route_hint(")
    i=text.index("{",start);depth=1;j=i+1
    while depth:
        depth+=(text[j]=="{")-(text[j]=="}");j+=1
    return text[start:j]

def generate_shopping_cash_hint_fixture(source,output):
    path=Path(output)/"shopping-cash-hint.generated.cpp"
    template=(Path(__file__).parent/"fixtures/shopping-cash-hint.cpp").read_text(encoding="utf8")
    path.write_text(template.replace("// EXACT_CASH_HINT",extract_shopping_cash_hint(source)),encoding="utf8")
    return path
