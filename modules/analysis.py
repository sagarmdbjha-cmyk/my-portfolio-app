"""
modules/analysis.py
━━━━━━━━━━━━━━━━━━
Technical & Fundamental Analysis:
  - RSI (Relative Strength Index)
  - Moving Averages (50-day, 200-day)
  - Buy / Hold / Exit signals
  - MF benchmark comparison
  - Loan payoff strategies (Avalanche & Snowball)
"""

import math
from typing import List, Dict, Any

try:
    import yfinance as yf
    import pandas as pd
    YFINANCE_OK = True
except ImportError:
    YFINANCE_OK = False


# ─────────────────────────────────────────────────────────────────────────────
# RSI Calculation (14-period standard)
# ─────────────────────────────────────────────────────────────────────────────

def _calc_rsi(prices: list, period: int = 14) -> float:
    """
    RSI calculate karo price list se.
    RSI > 70 = Overbought (EXIT signal)
    RSI < 30 = Oversold   (BUY signal)
    """
    if len(prices) < period + 1:
        return 50.0  # Neutral default

    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0
    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 1)


def _calc_ma(prices: list, period: int) -> float:
    """Simple moving average"""
    if len(prices) < period:
        return prices[-1] if prices else 0
    return sum(prices[-period:]) / period


# ─────────────────────────────────────────────────────────────────────────────
# SHARE SIGNAL GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def calculate_technical_signals(shares: List[Dict]) -> List[Dict]:
    """
    Har share ke liye technical analysis karo aur signal do:
    BUY / HOLD / EXIT / WATCH
    """
    results = []

    for share in shares:
        s = dict(share)
        buy_price  = s.get("buy_price", 0)
        curr_price = s.get("curr_price", buy_price)
        symbol     = s.get("symbol", "")
        pl_pct     = ((curr_price - buy_price) / buy_price * 100) if buy_price else 0

        # ── Try fetching historical data ──────
        rsi     = None
        ma50    = None
        ma200   = None
        hist_ok = False

        if YFINANCE_OK and symbol:
            try:
                yf_sym = symbol.upper()
                if not (yf_sym.endswith(".NS") or yf_sym.endswith(".BO")):
                    yf_sym += ".NS"
                ticker = yf.Ticker(yf_sym)
                hist   = ticker.history(period="1y")
                if not hist.empty and len(hist) > 20:
                    closes  = hist["Close"].tolist()
                    rsi     = _calc_rsi(closes)
                    ma50    = _calc_ma(closes, 50)
                    ma200   = _calc_ma(closes, 200)
                    hist_ok = True
            except Exception:
                pass

        # ── Signal Logic ──────────────────────
        signal = "HOLD"
        reasons = []

        # Rule 1: Bada loss → EXIT
        if pl_pct <= -20:
            signal = "EXIT"
            reasons.append(f"20%+ neeche ({pl_pct:.1f}%) — stop-loss")

        # Rule 2: RSI overbought → consider EXIT
        elif rsi and rsi > 72:
            signal = "EXIT"
            reasons.append(f"RSI {rsi} — overbought, exit consider karein")

        # Rule 3: RSI oversold → BUY opportunity
        elif rsi and rsi < 30:
            signal = "BUY"
            reasons.append(f"RSI {rsi} — oversold, achha entry point")

        # Rule 4: Price above MA50 and MA200 → Strong uptrend → BUY more
        elif hist_ok and ma50 and ma200 and curr_price > ma50 and curr_price > ma200:
            if pl_pct > 20:
                signal = "HOLD"
                reasons.append(f"Strong uptrend (MA50: ₹{ma50:.0f}), 20%+ up — hold karo")
            else:
                signal = "BUY"
                reasons.append(f"Price above MA50 ({ma50:.0f}) & MA200 ({ma200:.0f}) — bullish")

        # Rule 5: Price below MA50 → WATCH
        elif hist_ok and ma50 and curr_price < ma50:
            signal = "WATCH"
            reasons.append(f"MA50 (₹{ma50:.0f}) se neeche — wait karein")

        # Rule 6: Moderate profit → HOLD
        elif 5 <= pl_pct <= 20:
            signal = "HOLD"
            reasons.append(f"Healthy gain ({pl_pct:.1f}%) — hold karo")

        # Rule 7: Small loss (5-19%) → WATCH
        elif -20 < pl_pct < -5:
            signal = "WATCH"
            reasons.append(f"{pl_pct:.1f}% neeche — nazar rakho")

        # Fallback
        else:
            reasons.append(f"P&L: {pl_pct:+.1f}% — stable hold")

        s["signal"]  = signal
        s["rsi"]     = rsi if rsi else "N/A"
        s["ma50"]    = round(ma50, 2) if ma50 else None
        s["ma200"]   = round(ma200, 2) if ma200 else None
        s["reason"]  = " | ".join(reasons)
        results.append(s)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# MUTUAL FUND PERFORMANCE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

# Rough benchmark returns (annualized, approximate)
BENCHMARK_RETURNS = {
    "Nifty 50":           12.0,
    "Nifty Midcap 100":   15.0,
    "Nifty Smallcap 100": 14.0,
    "BSE Sensex":         11.5,
    "Nifty 500":          13.0,
}

def calculate_mf_performance(funds: List[Dict]) -> List[Dict]:
    """
    MF performance calculate karo aur benchmark se compare karo.
    Recommendation: HOLD / BUY (SIP continue) / SWITCH / WATCH
    """
    results = []
    for f in funds:
        f = dict(f)
        inv       = f.get("invested", 0)
        curr      = f.get("current_value", inv)
        benchmark = f.get("benchmark", "Nifty 50")
        bench_ret = BENCHMARK_RETURNS.get(benchmark, 12.0)

        actual_ret = ((curr - inv) / inv * 100) if inv else 0

        # Underperformance gap
        gap = actual_ret - bench_ret

        if actual_ret >= bench_ret:
            perf = "BUY"
            reason = f"Benchmark ({benchmark}) se {abs(gap):.1f}% zyada — SIP continue karein"
        elif actual_ret >= bench_ret * 0.7:   # 70% of benchmark
            perf = "HOLD"
            reason = f"Benchmark ke karib — {gap:.1f}% peeche, monitor karein"
        elif actual_ret >= 0:
            perf = "WATCH"
            reason = f"Benchmark se {abs(gap):.1f}% peeche — 3 mahine aur dekho"
        else:
            perf = "SWITCH"
            reason = f"Negative return ({actual_ret:.1f}%) — better fund consider karein"

        f["performance"]  = perf
        f["perf_reason"]  = reason
        f["return_pct"]   = round(actual_ret, 2)
        results.append(f)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# LOAN PAYOFF STRATEGIES
# ─────────────────────────────────────────────────────────────────────────────

def _months_to_payoff(outstanding: float, rate: float, emi: float) -> int:
    """Calculate karo kitne mahine mein loan khatam hoga"""
    if emi <= 0 or outstanding <= 0:
        return 0
    monthly_rate = rate / 12 / 100
    if monthly_rate == 0:
        return math.ceil(outstanding / emi)
    try:
        n = math.log(emi / (emi - outstanding * monthly_rate)) / math.log(1 + monthly_rate)
        return max(0, math.ceil(n))
    except Exception:
        return int(outstanding / emi) + 1


def _total_interest(outstanding: float, rate: float, emi: float) -> float:
    """Total interest calculate karo baaki tenure mein"""
    months = _months_to_payoff(outstanding, rate, emi)
    return max(0, (emi * months) - outstanding)


def avalanche_loan_strategy(loans: List[Dict], extra: float) -> str:
    """
    Avalanche Method: Sabse zyada interest rate wala loan pehle close karo.
    Most mathematically optimal — saves maximum interest.
    """
    if not loans:
        return "Koi loan nahi hai."

    sorted_loans = sorted(loans, key=lambda l: l.get("interest_rate", 0), reverse=True)

    lines = ["### ❄️ Avalanche Strategy (Maximum Interest Bachao)\n"]
    lines.append("**Kaise kaam karta hai:** Sabse zyada interest wale loan ko pehle target karo.\n")
    lines.append(f"**Extra payment available:** ₹{extra:,.0f}/month\n")
    lines.append("---\n")

    total_int_without = sum(_total_interest(l.get("outstanding",0),
                                            l.get("interest_rate",0),
                                            l.get("emi",0)) for l in loans)

    lines.append("**Priority Order:**\n")
    for rank, loan in enumerate(sorted_loans, 1):
        name    = loan.get("name", "Loan")
        rate    = loan.get("interest_rate", 0)
        bal     = loan.get("outstanding", 0)
        emi     = loan.get("emi", 0)
        months  = _months_to_payoff(bal, rate, emi)
        int_cost = _total_interest(bal, rate, emi)

        new_emi     = emi + (extra if rank == 1 else 0)
        new_months  = _months_to_payoff(bal, rate, new_emi)
        int_saved   = (months - new_months) * emi / 12

        lines.append(f"**#{rank} — {name}** ({rate}% p.a.)")
        lines.append(f"  - Outstanding: ₹{bal:,.0f}")
        lines.append(f"  - Normal payoff: {months} months mein")
        lines.append(f"  - Extra {extra:,.0f} se: {new_months} months mein ✅")
        lines.append(f"  - Interest bachega: ~₹{max(0, int_saved):,.0f}")
        lines.append("")

    lines.append(f"\n💡 **Total interest (bina extra):** ~₹{total_int_without:,.0f}")
    lines.append(f"💰 **Avalanche se faida:** Yeh strategy maximum interest bachati hai.")

    return "\n".join(lines)


def snowball_loan_strategy(loans: List[Dict], extra: float) -> str:
    """
    Snowball Method: Sabse chhota outstanding balance wala loan pehle close karo.
    Psychologically motivating — quick wins milte hain.
    """
    if not loans:
        return "Koi loan nahi hai."

    sorted_loans = sorted(loans, key=lambda l: l.get("outstanding", 0))

    lines = ["### ⛄ Snowball Strategy (Quick Wins, Motivation High Rakho)\n"]
    lines.append("**Kaise kaam karta hai:** Sabse chhota loan pehle close karo, phir woh EMI agle loan pe lagao.\n")
    lines.append(f"**Extra payment available:** ₹{extra:,.0f}/month\n")
    lines.append("---\n")

    freed_emi = extra
    lines.append("**Priority Order:**\n")

    for rank, loan in enumerate(sorted_loans, 1):
        name    = loan.get("name", "Loan")
        bal     = loan.get("outstanding", 0)
        rate    = loan.get("interest_rate", 0)
        emi     = loan.get("emi", 0)

        effective_emi = emi + freed_emi
        months        = _months_to_payoff(bal, rate, effective_emi)
        normal_months = _months_to_payoff(bal, rate, emi)

        lines.append(f"**#{rank} — {name}** (₹{bal:,.0f} outstanding)")
        lines.append(f"  - Interest rate: {rate}% p.a.")
        lines.append(f"  - Effective EMI: ₹{effective_emi:,.0f} (original + freed)")
        lines.append(f"  - Payoff: {months} months mein (normal: {normal_months})")
        lines.append(f"  - Jab close ho: ₹{effective_emi:,.0f} agle loan pe shift hoga ♻️")
        lines.append("")

        freed_emi += emi   # freed EMI next loan ke liye

    lines.append("💡 **Tip:** Jab ek loan close ho, uski puri EMI agle loan pe lagao — effect snowball ki tarah badhta hai!")
    lines.append(f"\n🎯 **Recommended:** Agar interest rate kaafi alag hai to Avalanche better hai. Motivation ke liye Snowball chunein.")

    return "\n".join(lines)
