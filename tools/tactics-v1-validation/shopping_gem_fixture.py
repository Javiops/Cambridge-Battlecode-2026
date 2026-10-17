"""Exact production completed-trip and bundle projection functions; real solo certificate."""
from pathlib import Path

def extract_shopping_gem(source):
    text=(Path(source)/"shopping.h").read_text(encoding="utf8")
    def block(token):
        start=text.index(token);i=text.index("{",start);depth=1;j=i+1
        while depth:
            depth+=(text[j]=="{")-(text[j]=="}");j+=1
        return text[start:j]+(";" if text[j:j+1]==";" else "")
    return "\n".join(block(token) for token in ("enum class ShopFamily","struct UpgradeDelta","struct GemReturnLegs","struct GemReturnPayoff","inline Actor project_bundle_actor(","inline GemReturnPayoff completed_gem_return("))

def generate_shopping_gem_fixture(source, output):
    destination=Path(output)/"shopping-gem.generated.cpp"
    destination.write_text((Path(__file__).parent/"fixtures/shopping-gem.cpp").read_text(encoding="utf8").replace("// EXACT_SHOPPING_GEM",extract_shopping_gem(source)),encoding="utf8")
    return destination
