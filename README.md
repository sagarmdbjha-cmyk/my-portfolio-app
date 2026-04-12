# 📊 Portfolio Manager Pro
### Aapka Complete Investment & Loan Tracker

---

## 🚀 Setup (Ek Baar Karna Hai)

### Step 1: Python Install Karein
Python 3.9+ chahiye. Check karein:
```
python --version
```
Agar nahi hai: https://www.python.org/downloads/

### Step 2: Folder kholein aur libraries install karein
```bash
cd portfolio_manager
pip install -r requirements.txt
```

### Step 3: App chalayein
```bash
streamlit run app.py
```
Browser automatically khulega: http://localhost:8501

---

## 📱 Features

| Feature | Kya karta hai |
|---------|---------------|
| 📈 Listed Shares | NSE/BSE live prices, RSI analysis, Buy/Hold/Exit |
| 🔒 Unlisted Shares | Manual price update, P&L track |
| 💼 Mutual Funds | NAV auto-update, benchmark comparison |
| 🏦 Loans | EMI tracker, Avalanche & Snowball strategy |
| 🏠 Master Dashboard | Total assets, liabilities, net worth |

---

## 🔄 Daily Use Kaise Karein

1. `streamlit run app.py` run karein
2. Sidebar mein **"Live Prices Update Karein"** dabayein
3. Agar MF hai to **"MF NAV Update Karein"** bhi dabayein
4. Master Dashboard mein apna net worth dekhein

---

## 💡 Technical Analysis (Share Signals)

| Signal | Condition |
|--------|-----------|
| 🟢 BUY MORE | RSI < 30 (oversold) ya strong uptrend (price > MA50 & MA200) |
| 🟡 HOLD | Healthy gain 5-20%, stable conditions |
| 🔴 EXIT | RSI > 72 (overbought) ya 20%+ loss |
| 🔵 WATCH | Price below MA50, ya 5-19% neeche |

**RSI (Relative Strength Index):**
- 0-30 → Oversold → Buy opportunity
- 30-70 → Normal range → Hold
- 70-100 → Overbought → Exit/Book profit

---

## 🏦 Loan Strategies

### Avalanche Method (Recommended)
- Sabse zyada interest wale loan ko pehle target karo
- Maximum interest bachata hai
- Mathematically best

### Snowball Method
- Sabse chhote balance wale loan ko pehle close karo
- Psychological motivation zyada
- Quick wins milte hain

---

## 📊 Mutual Fund Benchmark Comparison

| Performance | Condition |
|-------------|-----------|
| 🟢 BUY/Continue | Benchmark se zyada return |
| 🟡 HOLD | Benchmark ke 70-100% |
| 🔵 WATCH | Benchmark se thoda peeche |
| 🔴 SWITCH | Negative return, benchmark se bahut peeche |

---

## 🔑 Paytm Money API (Optional, Future Enhancement)

1. https://developer.paytmmoney.com/ pe jaiye
2. Apne Paytm Money account se login karein
3. "Create New App" → API Key & Secret milegi
4. App mein Settings → API Settings mein paste karein

**Note:** Abhi yfinance (Yahoo Finance) bilkul free kaam karta hai!
NSE/BSE prices real-time milte hain, koi API key nahi chahiye.

---

## 📁 File Structure

```
portfolio_manager/
├── app.py                  ← Main application (yahan se run karein)
├── requirements.txt        ← Libraries list
├── README.md               ← Yeh file
├── data/
│   └── portfolio.json      ← Aapka data (auto-save hota hai)
└── modules/
    ├── data_fetcher.py     ← Live prices fetch karta hai
    ├── analysis.py         ← RSI, signals, loan strategy
    └── data_store.py       ← Data save/load
```

---

## ❓ Common Problems

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"Price nahi mili"**
- NSE symbol check karein (e.g. TATAMOTORS, not Tata Motors)
- Internet connection check karein

**App band ho jaaye**
- Wahi folder mein `streamlit run app.py` dobara chalayein

---

*Made with ❤️ | Data auto-save hota hai portfolio.json mein*
