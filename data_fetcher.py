import requests
import json

# Naya deployment URL yahan daalein (Step 2 wala)
WEB_APP_URL = "APKA_NEW_DEPLOYMENT_URL"

def get_sheet_data(sheet_name):
    try:
        # URL parameters handle karne ka sahi tarika
        params = {'sheet': sheet_name}
        response = requests.get(WEB_APP_URL, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error fetching {sheet_name}: {e}")
        return []

def update_portfolio():
    # 'mutual fund' aur 'unlisted share' wahi naam rakhein jo Google Sheet ke tab ke hain
    mf_data = get_sheet_data("Mutual Fund")
    unlisted_data = get_sheet_data("unlisted share")
    
    # Baaki logic same rahega
    return {"mf": mf_data, "unlisted": unlisted_data}
