"""Read-only approval gate for future TradingAgents integration.

Input: one JSON document with technical_signal, ai_signal, confidence, and risk.
Output: JSON approval decision. Never connects to any broker.
"""
import json
import sys

VALID = {"BUY", "SELL", "HOLD"}

def review(data):
    tech = str(data.get("technical_signal", "")).upper()
    ai = str(data.get("ai_signal", "")).upper()
    risk = data.get("risk_ok") is True
    news = data.get("news_checked") is True
    historical = data.get("history_checked") is True
    if tech not in VALID or ai not in VALID:
        return {"approved": False, "decision": "REJECT", "reason": "missing_or_invalid_signal"}
    if tech not in ("BUY", "SELL"):
        return {"approved": False, "decision": "HOLD", "reason": "no_technical_entry"}
    if not (risk and news and historical):
        return {"approved": False, "decision": "REJECT", "reason": "incomplete_research_or_risk_check"}
    if tech != ai:
        return {"approved": False, "decision": "REJECT", "reason": "ai_disagrees"}
    return {"approved": True, "decision": tech, "reason": "research_agrees_and_risk_check_passed"}

if __name__ == "__main__":
    try:
        item = json.load(sys.stdin)
        result = review(item)
        print(json.dumps(result))
    except (ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"approved": False, "decision": "REJECT", "reason": "invalid_input"}))
        sys.exit(1)
