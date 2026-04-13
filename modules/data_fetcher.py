"""
modules/data_fetcher.py
=======================
app.py ye functions import karta hai:
  - fetch_live_prices(shares)   → Listed shares ke live NSE/BSE prices
  - fetch_mf_nav(mutual_funds)  → Mutual Fund ka latest NAV

Google Sheet se bhi data aata hai (unlisted + MF backup).
"""

import requests
import json
import time

# ─────────────────────────────────────────────────────────────
# GOOGLE SHEET WEB APP URL
# Apps Script > Deploy > Manage Deployments se copy karein
# ─────────────────────────────────────────────────────────────
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwcUs3M5LqWnuW5JAU7l6IzdkSpQ2SO4w4zfrgVtkHujqnJXCaAKVw_Xp7GRNZt4prLRw/exec"


# ═════════════════════════════════════════════════════════════
# 1.  GOOGLE SHEET HELPER
# ═════════════════════════════════════════════════════════════
def get_sheet_data(sheet_name: str) -> list:
    """
    Google Sheet tab se data fetch karta hai.
    Returns list of dicts (ek row = ek dict).
    """
    try:
        response = requests.get(
            WEB_APP_URL,
            params={"sheet": sheet_name},
            timeout=30,
            allow_redirects=True,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        print(f"[Sheet] Unexpected response for '{sheet_name}': {data}")
        return []
    except requests.exceptions.Timeout:
        print(f"[Sheet] Timeout fetching '{sheet_name}'")
        return []
    except requests.exceptions.ConnectionError:
        print(f"[Sheet] Network error fetching '{sheet_name}'")
        return []
    except json.JSONDecodeError as e:
        print(f"[Sheet] JSON error for '{sheet_name}': {e}")
        return []
    except Exception as e:
        print(f"[Sheet] Error fetching '{sheet_name}': {e}")
        return []


# ═════════════════════════════════════════════════════════════
# 2.  fetch_live_prices  ← app.py YAHI IMPORT KARTA HAI
# ═════════════════════════════════════════════════════════════
def fetch_live_prices(shares: list) -> list:
    """
    Listed shares ki current price NSE/BSE se fetch karta hai.
    yfinance use karta hai (free, no API key needed).
    """
    if not shares:
        return shares

    try:
        import yfinance as yf
    except ImportError:
        print("[Prices] yfinance not installed. Run: pip install yfinance")
        return shares

    updated = []
    for share in shares:
        symbol = share.get("symbol", "").strip().upper()
        if not symbol:
            updated.append(share)
            continue

        fetched = False
        for suffix in [".NS", ".BO"]:
            try:
                ticker = yf.Ticker(symbol + suffix)
                info   = ticker.fast_info
                price  = getattr(info, "last_price", None)

                if price and price > 0:
                    share = dict(share)
                    share["curr_price"] = round(float(price), 2)
                    print(f"[Prices] {symbol}{suffix} → ₹{share['curr_price']}")
                    fetched = True
                    break
            except Exception as e:
                print(f"[Prices] {symbol}{suffix} error: {e}")
                continue

        if not fetched:
            print(f"[Prices] Could not fetch price for {symbol}")

        updated.append(share)
        time.sleep(0.2)

    return updated


# ═════════════════════════════════════════════════════════════
# 3.  fetch_mf_nav  ← app.py YAHI IMPORT KARTA HAI
# ═════════════════════════════════════════════════════════════
def fetch_mf_nav(mutual_funds: list) -> list:
    """
    Mutual Funds ka latest NAV mfapi.in se fetch karta hai (free).
    """
    if not mutual_funds:
        return mutual_funds

    updated = []
    for fund in mutual_funds:
        scheme_code = str(fund.get("scheme_code", "")).strip()

        if not scheme_code:
            print(f"[NAV] No scheme code for: {fund.get('name', '?')}")
            updated.append(fund)
            continue

        try:
            url      = f"https://api.mfapi.in/mf/{scheme_code}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data     = response.json()

            if data.get("data") and len(data["data"]) > 0:
                latest_nav = float(data["data"][0]["nav"])
                fund = dict(fund)
                fund["curr_nav"]      = round(latest_nav, 4)
                fund["current_value"] = round(fund.get("units", 0) * latest_nav, 2)
                print(f"[NAV] {fund.get('name','?')} → NAV ₹{latest_nav}")
            else:
                print(f"[NAV] No data for scheme {scheme_code}")

        except requests.exceptions.Timeout:
            print(f"[NAV] Timeout for scheme {scheme_code}")
        except Exception as e:
            print(f"[NAV] Error for scheme {scheme_code}: {e}")

        updated.append(fund)
        time.sleep(0.1)

    return updated


# ═════════════════════════════════════════════════════════════
# 4.  GOOGLE SHEET SE PORTFOLIO UPDATE  (optional helper)
# ═════════════════════════════════════════════════════════════
def update_portfolio_from_sheet() -> dict:
    """
    Google Sheet se unlisted shares aur MF data pull karta hai.
    Settings page ya manual refresh ke liye call kar sakte hain.
    """
    # Unlisted Shares — sheet tab name exactly match karna chahiye
    unlisted_data = get_sheet_data("unlisted share")
    unlisted_out  = []
    for row in unlisted_data:
        try:
            unlisted_out.append({
                "name":       str(row.get("Company", row.get("Name", "Unknown"))).strip(),
                "qty":        float(row.get("Quantity", row.get("Qty", 0)) or 0),
                "cost_price": float(row.get("Cost Price", row.get("Buy Price", 0)) or 0),
                "est_price":  float(row.get("Est Price", row.get("Market Price", 0)) or 0),
                "status":     str(row.get("Status", "Hold")).strip(),
            })
        except Exception as e:
            print(f"[Sheet] Unlisted row parse error: {e} | row: {row}")

    # Mutual Funds — sheet tab name exactly match karna chahiye
    mf_data = get_sheet_data("Mutual Fund")
    mf_out  = []
    for row in mf_data:
        try:
            invested = float(row.get("Invested", row.get("Amount", 0)) or 0)
            buy_nav  = float(row.get("Buy NAV",  row.get("NAV", 1))    or 1)
            units    = invested / buy_nav if buy_nav else 0
            mf_out.append({
                "name":          str(row.get("Fund Name", row.get("Name", "Unknown"))).strip(),
                "scheme_code":   str(row.get("Scheme Code", "")).strip(),
                "invested":      invested,
                "buy_nav":       buy_nav,
                "curr_nav":      float(row.get("Current NAV", buy_nav) or buy_nav),
                "units":         round(units, 3),
                "current_value": float(row.get("Current Value", invested) or invested),
                "type":          str(row.get("Type", "SIP")).strip(),
                "category":      str(row.get("Category", "Other")).strip(),
                "benchmark":     str(row.get("Benchmark", "Nifty 50")).strip(),
            })
        except Exception as e:
            print(f"[Sheet] MF row parse error: {e} | row: {row}")

    return {
        "unlisted_shares": unlisted_out,
        "mutual_funds":    mf_out,
    }
