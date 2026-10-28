"""Adapt a completed TradingAgents full-state JSON into a fail-closed approval.
Does NOT connect to a broker or issue orders.
Usage: python evaluate_report.py path/to/full_states_log_DATE.json BUY
"""
import json, sys
from research_approval_gate import review

def evaluate(state, technical_signal):
    rating = str(state.get("final_rating", "")).strip().upper()
    # Rating is five-tier. Only explicit BUY/SELL can authorize an entry.
    ai_signal = rating if rating in ("BUY", "SELL") else "HOLD"
    evidence = {
        "technical_signal": technical_signal,
        "ai_signal": ai_signal,
        "news_checked": bool(str(state.get("news_report", "")).strip()),
        "history_checked": bool(str(state.get("market_report", "")).strip()),
        # A completed risk debate alone is not enough to verify portfolio risk limits.
        # Must be independently established by a future broker-specific risk engine.
        "risk_ok": False,
    }
    verdict = review(evidence)
    return {"report_rating": rating, "evidence": evidence,
            "approval": verdict, "execution_enabled": False}

if __name__ == "__main__":
    try:
        with open(sys.argv[1], encoding="utf-8") as fp:
            state = json.load(fp)
        print(json.dumps(evaluate(state, sys.argv[2]), indent=2))
    except (IndexError, OSError, ValueError) as exc:
        print(json.dumps({"approval": {"approved": False, "decision": "REJECT",
                          "reason": "report_unavailable_or_invalid"}, "execution_enabled": False}))
        sys.exit(1)
