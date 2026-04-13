import requests
import json

# Jo URL aapne abhi copy kiya tha, usse yahan quotes ke andar daalein
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwcUs3M5LqWnuW5JAU7l6IzdkSpQ2SO4w4zfrgVtkHujqnJXCaAKVw_Xp7GRNZt4prLRw/exec"

def get_sheet_data(sheet_name):
    try:
        response = requests.get(f"{WEB_APP_URL}?sheet={sheet_name}")
        return response.json()
    except Exception as e:
        print(f"Error fetching {sheet_name}: {e}")
        return []

def update_portfolio():
    # 1. Unlisted Shares automation
    unlisted_data = get_sheet_data("unlisted share")
    total_unlisted = sum(float(row.get('Amount', 0)) for row in unlisted_data)

    # 2. Mutual Fund automation
    mf_data = get_sheet_data("mutual fund")
    total_mf = sum(float(row.get('Current Value', 0)) for row in mf_data)

    return {
        "unlisted_balance": total_unlisted,
        "mf_balance": total_mf
    }
