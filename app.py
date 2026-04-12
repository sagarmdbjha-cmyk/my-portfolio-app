"""
╔══════════════════════════════════════════════════════════════╗
║         PORTFOLIO MANAGER PRO - Main Application            ║
║         Aapka complete investment tracker                   ║
╚══════════════════════════════════════════════════════════════╝

Run karne ke liye:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Internal modules
from modules.data_fetcher import fetch_live_prices, fetch_mf_nav
from modules.analysis import (
    calculate_technical_signals,
    calculate_mf_performance,
    avalanche_loan_strategy,
    snowball_loan_strategy
)
from modules.data_store import load_data, save_data, DEFAULT_DATA

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Manager Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2rem; font-weight: 700;
        background: linear-gradient(90deg, #1a73e8, #0d47a1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .metric-card {
        background: white; border-radius: 12px; padding: 1rem 1.2rem;
        border: 1px solid #e8eaed; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .badge-buy    { background:#e6f4ea; color:#137333; border-radius:20px;
                    padding:3px 10px; font-size:0.78rem; font-weight:600; }
    .badge-hold   { background:#fef7e0; color:#b05b00; border-radius:20px;
                    padding:3px 10px; font-size:0.78rem; font-weight:600; }
    .badge-exit   { background:#fce8e6; color:#c5221f; border-radius:20px;
                    padding:3px 10px; font-size:0.78rem; font-weight:600; }
    .badge-watch  { background:#e8f0fe; color:#1a73e8; border-radius:20px;
                    padding:3px 10px; font-size:0.78rem; font-weight:600; }
    .profit { color: #137333; font-weight: 600; }
    .loss   { color: #c5221f; font-weight: 600; }
    .section-divider { border-top: 2px solid #f0f0f0; margin: 1.5rem 0; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE - data load karo
# ─────────────────────────────────────────────
if "portfolio" not in st.session_state:
    st.session_state.portfolio = load_data()

portfolio = st.session_state.portfolio

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Portfolio Manager")
    st.markdown("---")
    page = st.radio(
        "Section chunein:",
        ["🏠 Master Dashboard",
         "📈 Listed Shares",
         "🔒 Unlisted Shares",
         "💼 Mutual Funds",
         "🏦 Loans & Debt",
         "⚙️ Settings & Data"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    if st.button("🔄 Live Prices Update Karein", use_container_width=True):
        with st.spinner("NSE/BSE se prices fetch ho rahe hain..."):
            updated = fetch_live_prices(portfolio["shares"])
            portfolio["shares"] = updated
            portfolio["last_updated"] = datetime.now().isoformat()
            save_data(portfolio)
            st.session_state.portfolio = portfolio
        st.success("✅ Prices update ho gaye!")
        st.rerun()

    if st.button("📊 MF NAV Update Karein", use_container_width=True):
        with st.spinner("Mutual Fund NAV fetch ho rahi hai..."):
            updated = fetch_mf_nav(portfolio["mutual_funds"])
            portfolio["mutual_funds"] = updated
            save_data(portfolio)
            st.session_state.portfolio = portfolio
        st.success("✅ NAV update ho gayi!")
        st.rerun()

    st.markdown("---")
    last_upd = portfolio.get("last_updated", "Kabhi nahi")
    if last_upd != "Kabhi nahi":
        try:
            dt = datetime.fromisoformat(last_upd)
            last_upd = dt.strftime("%d %b %Y, %I:%M %p")
        except Exception:
            pass
    st.caption(f"Last update: {last_upd}")


# ══════════════════════════════════════════════
# PAGE: MASTER DASHBOARD
# ══════════════════════════════════════════════
if page == "🏠 Master Dashboard":
    st.markdown('<p class="main-header">📊 Portfolio Master Dashboard</p>', unsafe_allow_html=True)
    st.caption("Aapke saare investments aur liabilities ek jagah")

    # ── Calculations ──────────────────────────
    shares = portfolio.get("shares", [])
    mf     = portfolio.get("mutual_funds", [])
    loans  = portfolio.get("loans", [])
    unl    = portfolio.get("unlisted_shares", [])

    total_share_inv  = sum(s.get("qty", 0) * s.get("buy_price", 0) for s in shares)
    total_share_curr = sum(s.get("qty", 0) * s.get("curr_price", s.get("buy_price", 0)) for s in shares)
    total_mf_inv     = sum(f.get("invested", 0) for f in mf)
    total_mf_curr    = sum(f.get("current_value", f.get("invested", 0)) for f in mf)
    total_unl_est    = sum(u.get("qty", 0) * u.get("est_price", 0) for u in unl)
    total_loan_bal   = sum(l.get("outstanding", 0) for l in loans)

    total_assets = total_share_curr + total_mf_curr + total_unl_est
    total_liab   = total_loan_bal
    net_worth    = total_assets - total_liab
    share_pl     = total_share_curr - total_share_inv

    # ── Top Metrics ───────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("💰 Total Assets", f"₹{total_assets:,.0f}",
                  delta=f"₹{share_pl:+,.0f} shares P&L")
    with c2:
        st.metric("🏦 Total Liabilities", f"₹{total_liab:,.0f}",
                  delta=f"{len(loans)} active loans", delta_color="inverse")
    with c3:
        delta_color = "normal" if net_worth >= 0 else "inverse"
        st.metric("🌟 Net Worth", f"₹{net_worth:,.0f}",
                  delta="Positive" if net_worth >= 0 else "Negative",
                  delta_color=delta_color)
    with c4:
        ratio = total_assets / total_liab if total_liab > 0 else float("inf")
        ratio_str = f"{ratio:.1f}x" if ratio != float("inf") else "∞ (No Debt)"
        st.metric("⚖️ Asset/Debt Ratio", ratio_str)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Master Table ──────────────────────────
    st.subheader("📋 Portfolio Snapshot")
    share_ret = ((total_share_curr - total_share_inv) / total_share_inv * 100) if total_share_inv else 0
    mf_ret    = ((total_mf_curr - total_mf_inv) / total_mf_inv * 100) if total_mf_inv else 0

    def _badge(signal):
        badges = {
            "BUY": '<span class="badge-buy">BUY MORE</span>',
            "HOLD": '<span class="badge-hold">HOLD</span>',
            "EXIT": '<span class="badge-exit">EXIT</span>',
            "WATCH": '<span class="badge-watch">WATCH</span>',
        }
        return badges.get(signal, signal)

    share_signal = "BUY" if share_ret > 15 else "EXIT" if share_ret < -10 else "HOLD"
    mf_signal    = "HOLD" if mf_ret >= 8 else "WATCH" if mf_ret >= 0 else "EXIT"
    loan_signal  = "EXIT" if total_liab > total_assets * 0.4 else "HOLD"

    master_html = f"""
    <table width="100%" style="border-collapse:collapse; font-size:0.9rem;">
      <thead>
        <tr style="background:#f8f9fa; border-bottom:2px solid #dee2e6;">
          <th align="left"  style="padding:10px 12px;">Category</th>
          <th align="right" style="padding:10px 12px;">Invested (₹)</th>
          <th align="right" style="padding:10px 12px;">Current Value (₹)</th>
          <th align="right" style="padding:10px 12px;">Return %</th>
          <th align="center"style="padding:10px 12px;">Signal</th>
        </tr>
      </thead>
      <tbody>
        <tr style="border-bottom:1px solid #f0f0f0;">
          <td style="padding:9px 12px;">📈 Listed Shares</td>
          <td align="right" style="padding:9px 12px;">₹{total_share_inv:,.0f}</td>
          <td align="right" style="padding:9px 12px;">₹{total_share_curr:,.0f}</td>
          <td align="right" style="padding:9px 12px;" class="{'profit' if share_ret>=0 else 'loss'}">{share_ret:+.1f}%</td>
          <td align="center" style="padding:9px 12px;">{_badge(share_signal)}</td>
        </tr>
        <tr style="border-bottom:1px solid #f0f0f0;">
          <td style="padding:9px 12px;">💼 Mutual Funds</td>
          <td align="right" style="padding:9px 12px;">₹{total_mf_inv:,.0f}</td>
          <td align="right" style="padding:9px 12px;">₹{total_mf_curr:,.0f}</td>
          <td align="right" style="padding:9px 12px;" class="{'profit' if mf_ret>=0 else 'loss'}">{mf_ret:+.1f}%</td>
          <td align="center" style="padding:9px 12px;">{_badge(mf_signal)}</td>
        </tr>
        <tr style="border-bottom:1px solid #f0f0f0;">
          <td style="padding:9px 12px;">🔒 Unlisted Shares</td>
          <td align="right" style="padding:9px 12px;">—</td>
          <td align="right" style="padding:9px 12px;">₹{total_unl_est:,.0f}</td>
          <td align="right" style="padding:9px 12px; color:#888;">Manual</td>
          <td align="center" style="padding:9px 12px;">{_badge("WATCH")}</td>
        </tr>
        <tr style="border-bottom:1px solid #f0f0f0; background:#fff5f5;">
          <td style="padding:9px 12px;">🏦 Loans (Liability)</td>
          <td align="right" style="padding:9px 12px; color:#c5221f;">-₹{total_loan_bal:,.0f}</td>
          <td align="right" style="padding:9px 12px; color:#c5221f;">-₹{total_loan_bal:,.0f}</td>
          <td align="right" style="padding:9px 12px;">—</td>
          <td align="center" style="padding:9px 12px;">{_badge(loan_signal)}</td>
        </tr>
        <tr style="background:#f8f9fa; font-weight:700; border-top:2px solid #dee2e6;">
          <td style="padding:10px 12px;">🌟 Net Worth</td>
          <td align="right" style="padding:10px 12px;">—</td>
          <td align="right" style="padding:10px 12px; color:{'#137333' if net_worth>=0 else '#c5221f'};">₹{net_worth:,.0f}</td>
          <td align="right" style="padding:10px 12px;">—</td>
          <td align="center" style="padding:10px 12px;">{'✅ On Track' if net_worth>0 else '⚠️ Review Karein'}</td>
        </tr>
      </tbody>
    </table>
    """
    st.markdown(master_html, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Charts ────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Assets Distribution")
        pie_data = {}
        if total_share_curr > 0: pie_data["Listed Shares"] = total_share_curr
        if total_mf_curr    > 0: pie_data["Mutual Funds"]  = total_mf_curr
        if total_unl_est    > 0: pie_data["Unlisted"]      = total_unl_est
        if pie_data:
            fig = px.pie(
                values=list(pie_data.values()),
                names=list(pie_data.keys()),
                color_discrete_sequence=["#1a73e8", "#34a853", "#fbbc04"],
                hole=0.4
            )
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data add karein")

    with col_b:
        st.subheader("Assets vs Liabilities")
        fig2 = go.Figure(go.Bar(
            x=["Total Assets", "Total Liabilities", "Net Worth"],
            y=[total_assets, total_liab, net_worth],
            marker_color=["#34a853", "#ea4335", "#1a73e8" if net_worth >= 0 else "#fbbc04"],
            text=[f"₹{v:,.0f}" for v in [total_assets, total_liab, net_worth]],
            textposition="outside"
        ))
        fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280,
                           yaxis_title="Amount (₹)", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Top Recommendations ───────────────────
    st.subheader("💡 AI Recommendations")
    r1, r2, r3 = st.columns(3)
    with r1:
        high_rate_loans = sorted(loans, key=lambda l: l.get("interest_rate", 0), reverse=True)
        if high_rate_loans:
            top = high_rate_loans[0]
            st.info(f"**Loan Priority:** '{top['name']}' ({top['interest_rate']}% p.a.) pehle close karein. Avalanche method use karein.")
        else:
            st.success("🎉 Koi loan nahi! Excellent!")
    with r2:
        losers = [s for s in shares if s.get("curr_price", s.get("buy_price", 0)) < s.get("buy_price", 0) * 0.85]
        if losers:
            st.warning(f"**Exit Alert:** {len(losers)} shares 15%+ neeche hain. Review karein: {', '.join(s['name'][:10] for s in losers[:3])}")
        else:
            st.success("✅ Koi bada loss nahi hai abhi.")
    with r3:
        if total_liab > 0 and total_liab > total_assets * 0.3:
            st.error("⚠️ **Debt High Hai!** Loan balance assets ka 30%+ hai. Aggressive repayment karein.")
        elif net_worth > 0:
            st.success(f"✅ **Healthy Net Worth!** ₹{net_worth:,.0f} positive hai.")
        else:
            st.warning("Portfolio abhi build ho raha hai. Keep investing!")


# ══════════════════════════════════════════════
# PAGE: LISTED SHARES
# ══════════════════════════════════════════════
elif page == "📈 Listed Shares":
    st.markdown('<p class="main-header">📈 Listed Shares</p>', unsafe_allow_html=True)

    shares = portfolio.get("shares", [])

    # ── Add new share ─────────────────────────
    with st.expander("➕ Naya Share Add Karein"):
        c1, c2, c3, c4 = st.columns(4)
        new_name   = c1.text_input("Company naam")
        new_symbol = c2.text_input("NSE Symbol (e.g. TATAMOTORS)")
        new_qty    = c3.number_input("Quantity", min_value=1, step=1)
        new_price  = c4.number_input("Buy Price (₹)", min_value=0.01, step=0.01)
        new_sector = st.selectbox("Sector", ["Energy","Finance","Tech","FMCG","Auto",
                                              "Infra","Telecom","Healthcare","Real Estate",
                                              "Mfg","Textile","Other"])
        if st.button("Share Add Karein"):
            if new_name and new_symbol and new_qty and new_price:
                shares.append({
                    "name": new_name, "symbol": new_symbol.upper(),
                    "qty": new_qty, "buy_price": float(new_price),
                    "curr_price": float(new_price), "sector": new_sector
                })
                portfolio["shares"] = shares
                save_data(portfolio)
                st.session_state.portfolio = portfolio
                st.success(f"✅ {new_name} add ho gaya!")
                st.rerun()
            else:
                st.error("Sabhi fields zaroor bharein")

    st.markdown("---")

    if not shares:
        st.info("Koi shares nahi hain. Upar se add karein ya Settings mein sample data load karein.")
    else:
        # ── Summary metrics ───────────────────
        total_inv  = sum(s.get("qty", 0) * s.get("buy_price", 0) for s in shares)
        total_curr = sum(s.get("qty", 0) * s.get("curr_price", s.get("buy_price", 0)) for s in shares)
        total_pl   = total_curr - total_inv
        ret_pct    = (total_pl / total_inv * 100) if total_inv else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Invested", f"₹{total_inv:,.0f}")
        c2.metric("Current Value", f"₹{total_curr:,.0f}")
        c3.metric("Total P&L", f"₹{total_pl:+,.0f}", f"{ret_pct:+.1f}%",
                  delta_color="normal" if total_pl >= 0 else "inverse")
        c4.metric("Holdings", str(len(shares)))

        st.markdown("---")
        st.subheader("Holdings with AI Signals")

        # ── Technical analysis ────────────────
        analyzed = calculate_technical_signals(shares)

        rows = []
        for s in analyzed:
            qty        = s.get("qty", 0)
            buy_p      = s.get("buy_price", 0)
            curr_p     = s.get("curr_price", buy_p)
            inv_val    = qty * buy_p
            curr_val   = qty * curr_p
            pl         = curr_val - inv_val
            pl_pct     = (pl / inv_val * 100) if inv_val else 0
            signal     = s.get("signal", "HOLD")
            rsi        = s.get("rsi", "—")
            reason     = s.get("reason", "")

            badge_map = {
                "BUY":  "🟢 BUY MORE",
                "HOLD": "🟡 HOLD",
                "EXIT": "🔴 EXIT",
                "WATCH":"🔵 WATCH"
            }

            rows.append({
                "Company":       s["name"],
                "Symbol":        s.get("symbol", ""),
                "Sector":        s.get("sector", ""),
                "Qty":           qty,
                "Buy ₹":         f"{buy_p:,.2f}",
                "Curr ₹":        f"{curr_p:,.2f}",
                "Invested":      f"₹{inv_val:,.0f}",
                "Curr Value":    f"₹{curr_val:,.0f}",
                "P&L":           f"{'+'if pl>=0 else ''}₹{pl:,.0f} ({pl_pct:+.1f}%)",
                "RSI":           str(rsi) if rsi != "—" else "—",
                "Signal":        badge_map.get(signal, signal),
                "Reason":        reason
            })

        df = pd.DataFrame(rows)

        # Color P&L column
        def color_pl(val):
            if "+" in str(val):
                return "color: #137333"
            elif val.startswith("-"):
                return "color: #c5221f"
            return ""

        st.dataframe(
            df,
            use_container_width=True,
            height=500,
            column_config={
                "Signal": st.column_config.TextColumn("Signal", width=120),
                "Reason": st.column_config.TextColumn("Analysis", width=200),
            },
            hide_index=True
        )

        # ── Delete a share ────────────────────
        st.markdown("---")
        del_col1, del_col2 = st.columns([3, 1])
        del_name = del_col1.selectbox("Share remove karein:", [s["name"] for s in shares])
        if del_col2.button("🗑 Remove"):
            portfolio["shares"] = [s for s in shares if s["name"] != del_name]
            save_data(portfolio)
            st.session_state.portfolio = portfolio
            st.rerun()

        # ── Sector chart ──────────────────────
        st.subheader("Sector-wise Allocation")
        sector_vals = {}
        for s in shares:
            sec = s.get("sector", "Other")
            val = s.get("qty", 0) * s.get("curr_price", s.get("buy_price", 0))
            sector_vals[sec] = sector_vals.get(sec, 0) + val
        fig = px.bar(
            x=list(sector_vals.keys()), y=list(sector_vals.values()),
            labels={"x": "Sector", "y": "Value (₹)"},
            color=list(sector_vals.values()),
            color_continuous_scale="Blues"
        )
        fig.update_layout(height=300, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════
# PAGE: UNLISTED SHARES
# ══════════════════════════════════════════════
elif page == "🔒 Unlisted Shares":
    st.markdown('<p class="main-header">🔒 Unlisted / Pre-IPO Shares</p>', unsafe_allow_html=True)
    st.info("ℹ️ Unlisted shares ki prices automatic nahi milti — yahan aap manually update kar sakte hain.")

    unl = portfolio.get("unlisted_shares", [])

    with st.expander("➕ Unlisted Share Add Karein"):
        c1, c2, c3 = st.columns(3)
        u_name  = c1.text_input("Company naam")
        u_qty   = c2.number_input("Quantity", min_value=1, step=1)
        u_cost  = c3.number_input("Cost price (₹)", min_value=0.0, step=0.01)
        c4, c5 = st.columns(2)
        u_est   = c4.number_input("Estimated market price (₹)", min_value=0.0, step=0.01)
        u_status= c5.selectbox("Status", ["Pre-IPO","IPO Pending","DRHP Filed","Listed Ho Gaya","Hold"])
        if st.button("Add Karein"):
            if u_name and u_qty:
                unl.append({"name": u_name, "qty": u_qty, "cost_price": float(u_cost),
                             "est_price": float(u_est), "status": u_status})
                portfolio["unlisted_shares"] = unl
                save_data(portfolio)
                st.session_state.portfolio = portfolio
                st.success("✅ Add ho gaya!")
                st.rerun()

    st.markdown("---")

    if not unl:
        st.info("Koi unlisted shares nahi hain abhi.")
    else:
        total_cost = sum(u.get("qty", 0) * u.get("cost_price", 0) for u in unl)
        total_est  = sum(u.get("qty", 0) * u.get("est_price", 0) for u in unl)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Cost", f"₹{total_cost:,.0f}")
        c2.metric("Est. Value", f"₹{total_est:,.0f}")
        c3.metric("Holdings", str(len(unl)))
        st.markdown("---")

        for i, u in enumerate(unl):
            col_a, col_b, col_c, col_d, col_e = st.columns([3, 1, 1, 1, 1])
            col_a.write(f"**{u['name']}** — {u.get('status','')}")
            col_b.write(f"Qty: {u.get('qty',0)}")
            new_est = col_c.number_input(
                "Est. price ₹", value=float(u.get("est_price", 0)),
                key=f"est_{i}", step=0.5, label_visibility="collapsed"
            )
            pl = (new_est - u.get("cost_price", 0)) * u.get("qty", 0)
            col_d.write(f"{'🟢' if pl >= 0 else '🔴'} ₹{pl:,.0f}")
            if col_e.button("Save", key=f"save_ul_{i}"):
                unl[i]["est_price"] = new_est
                portfolio["unlisted_shares"] = unl
                save_data(portfolio)
                st.session_state.portfolio = portfolio
                st.success("Saved!")
                st.rerun()


# ══════════════════════════════════════════════
# PAGE: MUTUAL FUNDS
# ══════════════════════════════════════════════
elif page == "💼 Mutual Funds":
    st.markdown('<p class="main-header">💼 Mutual Funds</p>', unsafe_allow_html=True)

    mf = portfolio.get("mutual_funds", [])

    with st.expander("➕ Mutual Fund Add Karein"):
        c1, c2 = st.columns(2)
        mf_name    = c1.text_input("Fund ka naam")
        mf_scheme  = c2.text_input("Scheme Code (AMFI se, e.g. 100016)")
        c3, c4, c5 = st.columns(3)
        mf_inv     = c3.number_input("Invested amount (₹)", min_value=0.0, step=100.0)
        mf_nav     = c4.number_input("Buy NAV (₹)", min_value=0.01, step=0.01)
        mf_type    = c5.selectbox("Type", ["SIP", "Lumpsum"])
        mf_cat     = st.selectbox("Category", ["Large Cap","Mid Cap","Small Cap",
                                                "Flexi Cap","ELSS","Debt","Index","Other"])
        mf_bench   = st.selectbox("Benchmark", ["Nifty 50","Nifty Midcap 100",
                                                 "Nifty Smallcap 100","BSE Sensex","Nifty 500"])
        if st.button("Fund Add Karein"):
            if mf_name and mf_inv and mf_nav:
                units = mf_inv / mf_nav
                mf.append({
                    "name": mf_name, "scheme_code": mf_scheme,
                    "invested": float(mf_inv), "buy_nav": float(mf_nav),
                    "curr_nav": float(mf_nav), "units": round(units, 3),
                    "current_value": float(mf_inv),
                    "type": mf_type, "category": mf_cat, "benchmark": mf_bench
                })
                portfolio["mutual_funds"] = mf
                save_data(portfolio)
                st.session_state.portfolio = portfolio
                st.success("✅ Fund add ho gaya!")
                st.rerun()

    st.markdown("---")

    if not mf:
        st.info("Koi mutual fund nahi hai. Upar se add karein.")
    else:
        total_inv  = sum(f.get("invested", 0) for f in mf)
        total_curr = sum(f.get("current_value", f.get("invested", 0)) for f in mf)
        total_pl   = total_curr - total_inv
        ret_pct    = (total_pl / total_inv * 100) if total_inv else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Invested", f"₹{total_inv:,.0f}")
        c2.metric("Current Value", f"₹{total_curr:,.0f}")
        c3.metric("Total Return", f"{ret_pct:+.1f}%",
                  delta="Above 8% = Good" if ret_pct >= 8 else "Below 8% = Review",
                  delta_color="normal" if ret_pct >= 8 else "inverse")

        st.markdown("---")
        analyzed_mf = calculate_mf_performance(mf)

        for f in analyzed_mf:
            inv   = f.get("invested", 0)
            curr  = f.get("current_value", inv)
            ret   = ((curr - inv) / inv * 100) if inv else 0
            perf  = f.get("performance", "HOLD")
            units = f.get("units", 0)
            curr_nav = f.get("curr_nav", f.get("buy_nav", 0))

            badge_color = {"HOLD": "🟡", "BUY": "🟢", "SWITCH": "🔴", "WATCH": "🔵"}
            icon = badge_color.get(perf, "🟡")

            with st.container():
                ca, cb, cc, cd = st.columns([3, 1, 1, 1])
                ca.markdown(f"**{f['name']}**  \n{f.get('category','')} | {f.get('benchmark','')}")
                cb.metric("Invested", f"₹{inv:,.0f}")
                cc.metric("Current", f"₹{curr:,.0f}", f"{ret:+.1f}%",
                          delta_color="normal" if ret >= 0 else "inverse")
                cd.markdown(f"**{icon} {perf}**  \n_{f.get('perf_reason','')}_")
                st.progress(min(max((ret + 50) / 100, 0), 1))
                st.markdown("---")


# ══════════════════════════════════════════════
# PAGE: LOANS
# ══════════════════════════════════════════════
elif page == "🏦 Loans & Debt":
    st.markdown('<p class="main-header">🏦 Loan & Debt Manager</p>', unsafe_allow_html=True)

    loans = portfolio.get("loans", [])

    with st.expander("➕ Naya Loan Add Karein"):
        c1, c2 = st.columns(2)
        ln_name  = c1.text_input("Loan ka naam")
        ln_type  = c2.selectbox("Type", ["Personal Loan","Home Loan","Car Loan",
                                          "Education Loan","Business Loan","Credit Card"])
        c3, c4, c5 = st.columns(3)
        ln_total   = c3.number_input("Total amount (₹)", min_value=0.0, step=1000.0)
        ln_out     = c4.number_input("Outstanding (₹)", min_value=0.0, step=1000.0)
        ln_rate    = c5.number_input("Interest rate (% p.a.)", min_value=0.0, step=0.1)
        c6, c7 = st.columns(2)
        ln_emi     = c6.number_input("Monthly EMI (₹)", min_value=0.0, step=100.0)
        ln_months  = c7.number_input("Baki mahine", min_value=1, step=1)
        if st.button("Loan Add Karein"):
            if ln_name and ln_total and ln_out:
                loans.append({
                    "name": ln_name, "type": ln_type,
                    "total_amount": float(ln_total), "outstanding": float(ln_out),
                    "interest_rate": float(ln_rate), "emi": float(ln_emi),
                    "remaining_months": int(ln_months)
                })
                portfolio["loans"] = loans
                save_data(portfolio)
                st.session_state.portfolio = portfolio
                st.success("✅ Loan add ho gaya!")
                st.rerun()

    st.markdown("---")

    if not loans:
        st.success("🎉 Koi loan nahi hai! Aap debt-free hain.")
    else:
        total_bal  = sum(l.get("outstanding", 0) for l in loans)
        total_emi  = sum(l.get("emi", 0) for l in loans)
        total_int  = sum(l.get("outstanding", 0) * l.get("interest_rate", 0) / 100 for l in loans)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Debt", f"₹{total_bal:,.0f}")
        c2.metric("Monthly EMI", f"₹{total_emi:,.0f}")
        c3.metric("Annual Interest Cost", f"₹{total_int:,.0f}")
        c4.metric("Active Loans", str(len(loans)))

        # ── Loan cards ────────────────────────
        st.markdown("---")
        st.subheader("Individual Loans")
        for i, l in enumerate(loans):
            paid_pct = ((l.get("total_amount", 1) - l.get("outstanding", 0)) /
                        l.get("total_amount", 1) * 100)
            rate = l.get("interest_rate", 0)
            color = "🔴" if rate > 12 else "🟡" if rate > 9 else "🟢"
            with st.container():
                ca, cb, cc = st.columns([2, 2, 1])
                ca.markdown(f"**{l['name']}** ({l.get('type','')})")
                ca.markdown(f"{color} {rate}% p.a. | EMI: ₹{l.get('emi',0):,.0f}/mo")
                cb.markdown(f"Outstanding: **₹{l.get('outstanding',0):,.0f}**")
                cb.progress(paid_pct / 100)
                cb.caption(f"{paid_pct:.0f}% repaid")
                if cc.button("🗑 Delete", key=f"del_loan_{i}"):
                    loans.pop(i)
                    portfolio["loans"] = loans
                    save_data(portfolio)
                    st.session_state.portfolio = portfolio
                    st.rerun()
                st.markdown("---")

        # ── Payoff Strategies ─────────────────
        st.subheader("🧮 Debt Payoff Strategy")
        tab1, tab2 = st.tabs(["❄️ Avalanche Method (Sabse Zyada Interest Pehle)",
                               "⛄ Snowball Method (Sabse Chhota Loan Pehle)"])
        extra_payment = st.number_input(
            "Har mahine extra kitna pay kar sakte hain? (₹)", min_value=0.0, step=500.0, value=5000.0
        )

        with tab1:
            plan = avalanche_loan_strategy(loans, extra_payment)
            st.markdown(plan)

        with tab2:
            plan2 = snowball_loan_strategy(loans, extra_payment)
            st.markdown(plan2)


# ══════════════════════════════════════════════
# PAGE: SETTINGS
# ══════════════════════════════════════════════
elif page == "⚙️ Settings & Data":
    st.markdown('<p class="main-header">⚙️ Settings & Data Management</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📥 Sample Data Load Karein",
                                  "💾 Export / Import",
                                  "🔑 API Settings"])

    with tab1:
        st.markdown("Aapke PDF se extracted share data load karne ke liye:")
        if st.button("📊 Aapka Portfolio Load Karein (PDF Data)", use_container_width=True):
            from modules.data_store import DEFAULT_DATA
            portfolio.update(DEFAULT_DATA)
            save_data(portfolio)
            st.session_state.portfolio = portfolio
            st.success("✅ Aapka portfolio data load ho gaya! Ab 'Live Prices Update Karein' dabayein.")
            st.rerun()

        if st.button("🗑 Saara Data Reset Karein", use_container_width=True):
            from modules.data_store import DEFAULT_DATA
            empty = {"shares": [], "unlisted_shares": [], "mutual_funds": [],
                     "loans": [], "last_updated": ""}
            save_data(empty)
            st.session_state.portfolio = empty
            st.warning("Data reset ho gaya.")
            st.rerun()

    with tab2:
        st.markdown("**Current data download karein:**")
        data_json = json.dumps(portfolio, indent=2, ensure_ascii=False)
        st.download_button("⬇️ JSON Download Karein", data_json,
                           "portfolio_backup.json", "application/json")

        st.markdown("---")
        st.markdown("**Backup se restore karein:**")
        uploaded = st.file_uploader("JSON file upload karein", type=["json"])
        if uploaded:
            try:
                data = json.load(uploaded)
                save_data(data)
                st.session_state.portfolio = data
                st.success("✅ Data restore ho gaya!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    with tab3:
        st.markdown("""
        ### Paytm Money API Setup

        1. **developer.paytmmoney.com** pe jaiye
        2. Apne Paytm Money account se login karein
        3. "Create New App" → API Key aur Secret copy karein
        4. Neeche paste karein:
        """)
        api_key    = st.text_input("Paytm Money API Key", type="password",
                                   value=portfolio.get("settings", {}).get("pm_api_key", ""))
        api_secret = st.text_input("Paytm Money API Secret", type="password",
                                   value=portfolio.get("settings", {}).get("pm_api_secret", ""))
        if st.button("Save API Settings"):
            if "settings" not in portfolio:
                portfolio["settings"] = {}
            portfolio["settings"]["pm_api_key"]    = api_key
            portfolio["settings"]["pm_api_secret"] = api_secret
            save_data(portfolio)
            st.session_state.portfolio = portfolio
            st.success("✅ API settings save ho gayi!")

        st.markdown("---")
        st.info("""
        **Agar Paytm Money API na mile toh:**
        yfinance automatically NSE/BSE data fetch karta hai — bilkul free!
        Sidebar mein 'Live Prices Update Karein' button click karein.
        """)
