"""
modules/data_fetcher.py
━━━━━━━━━━━━━━━━━━━━━
Live price fetch karne ke liye:
  - Listed shares → yfinance (Yahoo Finance, free)
  - Mutual Funds  → mftool  (AMFI India, free)
"""

import time
import random
from datetime import datetime

# ─── yfinance import ─────────────────────────────────────────────────────────
try:
    import yfinance as yf
    YFINANCE_OK = True
except ImportError:
    YFINANCE_OK = False

# ─── mftool import ───────────────────────────────────────────────────────────
try:
    from mftool import Mftool
    mf_tool = Mftool()
    MFTOOL_OK = True
except ImportError:
    mf_tool = None
    MFTOOL_OK = False


# ─────────────────────────────────────────────────────────────────────────────
# NSE symbol mapping
# Yahoo Finance mein NSE symbols ke saath ".NS" lagta hai
# ─────────────────────────────────────────────────────────────────────────────
SYMBOL_MAP = {
    # Aapke portfolio ke symbols
    "ADANIGAS":       "ADANIGAS.NS",
    "ADANIPOWER":     "ADANIPOWER.NS",
    "AVENUESI":       "AVENUESI.NS",
    "GAIL":           "GAIL.NS",
    "GTLINFRA":       "GTLINFRA.NS",
    "IRB":            "IRB.NS",
    "IRFC":           "IRFC.NS",
    "ITC":            "ITC.NS",
    "JIOFIN":         "JIOFIN.NS",
    "MISHTANN":       "MISHTANN.NS",
    "NTPCGREEN":      "NTPCGREEN.NS",
    "ORIENTGREEN":    "ORIENTGREEN.NS",
    "SUZLON":         "SUZLON.NS",
    "TATAMOTORS":     "TATAMOTORS.NS",
    "TATATECH":       "TATATECH.NS",
    "VODAFONEIDEA":   "IDEA.NS",
    "WIPRO":          "WIPRO.NS",
    "XCHANGING":      "XCHANGING.NS",
    "YESBANK":        "YESBANK.NS",
    "BEL":            "BEL.NS",
    "ADANIENSOL":     "ADANIENSOL.NS",
    "RATTANINDIA":    "RTNINDIA.NS",
    "BPCL":           "BPCL.NS",
    "VEDL":           "VEDL.NS",
    "AKSHAR":         "AKSHARSPINTEX.NS",
    "TATIA":          "TATIAGLOBAL.NS",
    "VIDYAWIRES":     "VIDYAWIRES.NS",
}


def _get_yf_symbol(share: dict) -> str:
    """Share dict se Yahoo Finance symbol nikalo"""
    symbol = share.get("symbol", "").upper().strip()
    # Direct match
    if symbol in SYMBOL_MAP:
        return SYMBOL_MAP[symbol]
    # Already has .NS or .BO
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol
    # Default: .NS lagao
    return symbol + ".NS"


def fetch_live_prices(shares: list) -> list:
    """
    Har share ki live price fetch karo yfinance se.
    Agar yfinance kaam na kare, existing price rakho.
    """
    if not shares:
        return shares

    if not YFINANCE_OK:
        print("⚠️  yfinance install nahi hai. 'pip install yfinance' run karein.")
        return _simulate_prices(shares)

    updated = []
    for share in shares:
        yf_sym = _get_yf_symbol(share)
        try:
            ticker = yf.Ticker(yf_sym)
            # Fast price fetch — 1d history ka last close
            hist = ticker.history(period="1d", interval="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
                share = dict(share)  # copy
                share["curr_price"]    = round(price, 2)
                share["price_source"]  = "Yahoo Finance"
                share["price_updated"] = datetime.now().isoformat()
                print(f"  ✅ {share.get('name','?')} ({yf_sym}): ₹{price:.2f}")
            else:
                print(f"  ⚠️  {share.get('name','?')} ({yf_sym}): Data nahi mila")
        except Exception as e:
            print(f"  ❌ {share.get('name','?')} ({yf_sym}): Error — {e}")
        updated.append(share)
        time.sleep(0.2)          # Rate limit se bachne ke liye

    return updated


def fetch_mf_nav(funds: list) -> list:
    """
    Mutual Fund ka current NAV fetch karo mftool se.
    scheme_code chahiye (AMFI code) — e.g. "100016" for SBI Bluechip.
    """
    if not funds:
        return funds

    if not MFTOOL_OK:
        print("⚠️  mftool install nahi hai. 'pip install mftool' run karein.")
        return funds

    updated = []
    for f in funds:
        scheme_code = str(f.get("scheme_code", "")).strip()
        if not scheme_code:
            updated.append(f)
            continue
        try:
            data = mf_tool.get_scheme_quote(scheme_code)
            if data and "nav" in data:
                nav = float(data["nav"])
                f = dict(f)
                f["curr_nav"]       = round(nav, 4)
                f["current_value"]  = round(f.get("units", 0) * nav, 2)
                f["nav_date"]       = data.get("date", "")
                f["nav_updated"]    = datetime.now().isoformat()
                print(f"  ✅ {f.get('name','?')}: NAV ₹{nav:.4f}")
        except Exception as e:
            print(f"  ❌ {f.get('name','?')}: Error — {e}")
        updated.append(f)

    return updated


def _simulate_prices(shares: list) -> list:
    """
    Fallback: yfinance na ho toh ±3% random variation se simulate karo.
    Demo purpose ke liye.
    """
    updated = []
    for s in shares:
        s = dict(s)
        base = s.get("curr_price", s.get("buy_price", 100))
        variation = random.uniform(-0.03, 0.03)
        s["curr_price"]   = round(base * (1 + variation), 2)
        s["price_source"] = "Simulated"
        updated.append(s)
    return updated


def search_mf_schemes(query: str) -> list:
    """
    Mutual fund dhundho AMFI database mein.
    Returns: list of (scheme_code, scheme_name)
    """
    if not MFTOOL_OK:
        return []
    try:
        results = mf_tool.search_scheme_by_name(query)
        return [(code, name) for name, code in results.items()][:10]
    except Exception:
        return []
