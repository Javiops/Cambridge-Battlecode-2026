"""Exact named-return and accepted-purchase checks with explicit SDK adapters."""
from pathlib import Path


def extract_shopping_investment(source):
    text = (Path(source) / "shopping.h").read_text(encoding="utf8")

    def block(start):
        opening = text.index("{", start)
        depth, end = 1, opening + 1
        while depth:
            depth += (text[end] == "{") - (text[end] == "}")
            end += 1
        return text[start:end] + (";" if text[end:end+1] == ";" else "")

    tokens = ["enum class ShopFamily", "enum class ShopStat", "struct ShopInventory"]
    if "struct CashInvestment" in text:
        tokens.append("struct CashInvestment")
    tokens += ["struct ShoppingState", "struct UpgradeDelta", "struct ReturnPayoff"]
    types = "\n".join(block(text.index(token)) for token in tokens)
    functions = "\n".join(block(text.rfind("inline ", 0, text.index(name))) for name in
                          ("upgrade_delta(", "upgrade_mission_value(", "named_return_payoff(", "clear_investment(",
                           "investment_plan_invalid(", "shopping_after_action("))
    return types, functions


def generate_shopping_investment_fixture(source, output):
    types, functions = extract_shopping_investment(source)
    template = Path(__file__).parent / "fixtures" / "shopping-investment.cpp"
    destination = Path(output) / "shopping-investment.generated.cpp"
    destination.write_text(template.read_text(encoding="utf8").replace(
        "// EXACT_SHOP_TYPES", types).replace("// EXACT_SHOP_FUNCTIONS", functions), encoding="utf8")
    return destination
