"""Exact finite cash acquisition plus completed gem itinerary; actual solo model."""
from pathlib import Path
from shopping_gem_fixture import extract_shopping_gem

def extract_shopping_cash(source):
    text=(Path(source)/"shopping.h").read_text(encoding="utf8")
    def block(token):
        start=text.index(token);i=text.index("{",start);depth=1;j=i+1
        while depth:
            depth+=(text[j]=="{")-(text[j]=="}");j+=1
        return text[start:j]+(";"if text[j:j+1]==";"else"")
    return extract_shopping_gem(source)+"\n"+"\n".join(block(token)for token in
        ("struct CashGemLegs","struct CashGemPayoff","struct CashInvestment","inline CashGemPayoff completed_cash_gem(","inline bool cash_reward_paid("))

def generate_shopping_cash_fixture(source,output):
    target=Path(output)/"shopping-cash.generated.cpp"
    template=(Path(__file__).parent/"fixtures/shopping-cash.cpp").read_text(encoding="utf8")
    target.write_text(template.replace("// EXACT_CASH_POLICY",extract_shopping_cash(source)),encoding="utf8")
    return target
