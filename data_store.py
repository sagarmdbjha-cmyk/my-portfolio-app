"""
modules/data_store.py
━━━━━━━━━━━━━━━━━━━━
Portfolio data ko JSON file mein save/load karo.
Aapke PDF se extracted data yahan pre-loaded hai.
"""

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "portfolio.json")

# ─────────────────────────────────────────────────────────────────────────────
# Aapka portfolio data (PDF se extracted)
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_DATA = {
    "shares": [
        {"name": "Adani Gas",           "symbol": "ADANIGAS",    "qty": 40,    "buy_price": 737.96, "curr_price": 737.96, "sector": "Energy"},
        {"name": "Adani Power",         "symbol": "ADANIPOWER",  "qty": 1,     "buy_price": 147.62, "curr_price": 147.62, "sector": "Energy"},
        {"name": "AKSHAR SPINTEX",      "symbol": "AKSHAR",      "qty": 151,   "buy_price": 0.66,   "curr_price": 0.66,   "sector": "Textile"},
        {"name": "AvenuesAI Limited",   "symbol": "AVENUESI",    "qty": 5000,  "buy_price": 15.67,  "curr_price": 15.67,  "sector": "Tech"},
        {"name": "GAIL",                "symbol": "GAIL",        "qty": 1,     "buy_price": 169.88, "curr_price": 169.88, "sector": "Energy"},
        {"name": "GTL Infra",           "symbol": "GTLINFRA",    "qty": 10100, "buy_price": 1.27,   "curr_price": 1.27,   "sector": "Telecom"},
        {"name": "IRB Infra",           "symbol": "IRB",         "qty": 2500,  "buy_price": 54.81,  "curr_price": 54.81,  "sector": "Infra"},
        {"name": "IRFC",                "symbol": "IRFC",        "qty": 730,   "buy_price": 136.21, "curr_price": 136.21, "sector": "Finance"},
        {"name": "ITC",                 "symbol": "ITC",         "qty": 50,    "buy_price": 307.58, "curr_price": 307.58, "sector": "FMCG"},
        {"name": "JIO Financial",       "symbol": "JIOFIN",      "qty": 100,   "buy_price": 243.89, "curr_price": 243.89, "sector": "Finance"},
        {"name": "Mishtann Foods",      "symbol": "MISHTANN",    "qty": 150,   "buy_price": 3.69,   "curr_price": 3.69,   "sector": "FMCG"},
        {"name": "NTPC Green Energy",   "symbol": "NTPCGREEN",   "qty": 271,   "buy_price": 94.72,  "curr_price": 94.72,  "sector": "Energy"},
        {"name": "Orient Green Power",  "symbol": "ORIENTGREEN", "qty": 8020,  "buy_price": 13.60,  "curr_price": 13.60,  "sector": "Energy"},
        {"name": "Suzlon",              "symbol": "SUZLON",      "qty": 475,   "buy_price": 53.39,  "curr_price": 53.39,  "sector": "Energy"},
        {"name": "Tata Motors CV",      "symbol": "TATAMOTORS",  "qty": 10,    "buy_price": 319.72, "curr_price": 319.72, "sector": "Auto"},
        {"name": "Tata Motors PV",      "symbol": "TATAMOTORS",  "qty": 20,    "buy_price": 519.98, "curr_price": 519.98, "sector": "Auto"},
        {"name": "Tata Technologies",   "symbol": "TATATECH",    "qty": 150,   "buy_price": 884.09, "curr_price": 884.09, "sector": "Tech"},
        {"name": "Tatia Global",        "symbol": "TATIA",       "qty": 170,   "buy_price": 2.97,   "curr_price": 2.97,   "sector": "Real Estate"},
        {"name": "VIDYA WIRES",         "symbol": "VIDYAWIRES",  "qty": 200,   "buy_price": 49.67,  "curr_price": 49.67,  "sector": "Mfg"},
        {"name": "Vodafone IDEA",       "symbol": "VODAFONEIDEA","qty": 100,   "buy_price": 7.81,   "curr_price": 7.81,   "sector": "Telecom"},
        {"name": "Wipro",               "symbol": "WIPRO",       "qty": 100,   "buy_price": 190.98, "curr_price": 190.98, "sector": "Tech"},
        {"name": "Xchanging Solutions", "symbol": "XCHANGING",   "qty": 2500,  "buy_price": 106.22, "curr_price": 106.22, "sector": "Tech"},
        {"name": "Yes Bank",            "symbol": "YESBANK",     "qty": 1,     "buy_price": 22.32,  "curr_price": 22.32,  "sector": "Finance"},
    ],
    "unlisted_shares": [],
    "mutual_funds": [],
    "loans": [],
    "settings": {},
    "last_updated": ""
}


def load_data() -> dict:
    """JSON file se portfolio load karo. Na ho toh DEFAULT_DATA return karo."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Nayi keys merge karo agar missing hain
            for key in DEFAULT_DATA:
                if key not in data:
                    data[key] = DEFAULT_DATA[key]
            return data
        except Exception as e:
            print(f"Data load error: {e} — default data use ho raha hai")
    return dict(DEFAULT_DATA)


def save_data(data: dict) -> bool:
    """Portfolio JSON file mein save karo."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False
