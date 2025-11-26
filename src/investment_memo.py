# Investment memo module for the prediction market fund
import markdown

def generate_investment_memo(market_id, decision, ev, conviction, sources):
    """
    Generates an investment memo in markdown format.
    """
    memo = f"""
# Investment Memo

**Market ID:** {market_id}
**Decision:** {decision}
**Expected Value:** {ev}
**Conviction:** {conviction}
**Sources:**

"""
    for source in sources:
        memo += f"- {source}\n"

    return markdown.markdown(memo)

