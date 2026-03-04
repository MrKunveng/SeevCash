import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os

st.set_page_config(
    page_title="SeevCash - Investor Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = {
    "primary": "#6C63FF",
    "secondary": "#00D2FF",
    "accent": "#FF6584",
    "success": "#00C853",
    "warning": "#FFB300",
    "dark": "#1A1A2E",
    "card_bg": "#16213E",
    "text": "#E8E8E8",
    "grid": "rgba(255,255,255,0.05)",
    "ghs": "#FFB300",
    "usd": "#00D2FF",
}

CHANNEL_COLORS = {
    "Pay to MoMo": "#FF6584",
    "Add from MoMo": "#00C853",
    "Withdraw to MoMo": "#6C63FF",
    "Mobile Requests": "#FFB300",
    "Pay to Banks": "#E040FB",
    "SeevPlus Withdrawals": "#FF5722",
    "SeevAPI Transactions": "#00D2FF",
    "P2P Transfers": "#FFEE58",
    "Cross-border": "#AB47BC",
    "On-chain Deposits": "#26A69A",
    "On-chain Withdrawals": "#42A5F5",
}

GHS_CHANNELS = {
    "Pay to MoMo": "pay_to_momo",
    "Add from MoMo": "add_from_momo",
    "Withdraw to MoMo": "withdraw_to_momo",
    "Mobile Requests": "mobile_request",
    "Pay to Banks": "pay_to_banks",
    "SeevPlus Withdrawals": "seevplus_withdraw",
    "SeevAPI Transactions": "api_txn",
    "P2P Transfers": "pay_to_users",
    "Cross-border": "cross_border",
}
USD_CHANNELS = {
    "On-chain Deposits": "onchain_deposit",
    "On-chain Withdrawals": "onchain_withdraw",
}
ALL_CHANNELS = {**GHS_CHANNELS, **USD_CHANNELS}

CHANNEL_META = {
    "Pay to MoMo": {
        "prefix": "pay_to_momo", "currency": "GHS", "source": "paytomomos.csv",
        "description": "Outbound payments from SeevCash wallets to Mobile Money (MTN MoMo, Vodafone Cash, AirtelTigo) recipients.",
        "has_fees": True, "has_count": True,
    },
    "Add from MoMo": {
        "prefix": "add_from_momo", "currency": "GHS", "source": "adding_money_from_momo.csv",
        "description": "Inbound deposits — users funding their SeevCash wallet from Mobile Money accounts.",
        "has_fees": True, "has_count": True,
    },
    "Withdraw to MoMo": {
        "prefix": "withdraw_to_momo", "currency": "GHS", "source": "withdrawmoneytomomos.csv",
        "description": "Withdrawals from SeevCash wallet to user's Mobile Money account.",
        "has_fees": True, "has_count": True,
    },
    "Mobile Requests": {
        "prefix": "mobile_request", "currency": "GHS", "source": "transaction_from_request_mobile.csv",
        "description": "Transactions initiated via mobile payment requests between users.",
        "has_fees": True, "has_count": True,
    },
    "Pay to Banks": {
        "prefix": "pay_to_banks", "currency": "GHS", "source": "paytobanks.csv",
        "description": "Outbound transfers from SeevCash wallets to local bank accounts.",
        "has_fees": True, "has_count": True,
    },
    "SeevPlus Withdrawals": {
        "prefix": "seevplus_withdraw", "currency": "GHS", "source": "transactions___seevplus_withdraw.csv",
        "description": "Withdrawals from SeevPlus savings/investment product.",
        "has_fees": True, "has_count": True,
    },
    "SeevAPI Transactions": {
        "prefix": "api_txn", "currency": "GHS", "source": "apitransactions.csv",
        "description": "Transactions from SeevAPI customers — programmatic merchant and B2B integrations.",
        "has_fees": False, "has_count": True,
    },
    "P2P Transfers": {
        "prefix": "pay_to_users", "currency": "GHS", "source": "sum_of_transaction_paytousers.csv",
        "description": "Peer-to-peer transfers between SeevCash users (P2P payments).",
        "has_fees": False, "has_count": True,
    },
    "Cross-border": {
        "prefix": "cross_border", "currency": "GHS", "source": "cross_border_transactions.csv",
        "description": "Cross-border remittance and international payment transactions.",
        "has_fees": False, "has_count": False,
    },
    "On-chain Deposits": {
        "prefix": "onchain_deposit", "currency": "USD", "source": "onchaintransactions__deposit.csv",
        "description": "Cryptocurrency deposits onto the SeevCash platform (USDT/USDC on-chain).",
        "has_fees": True, "has_count": False,
    },
    "On-chain Withdrawals": {
        "prefix": "onchain_withdraw", "currency": "USD", "source": "onchaintransactions__withdraw.csv",
        "description": "Cryptocurrency withdrawals from SeevCash to external wallets.",
        "has_fees": True, "has_count": True,
    },
}

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    .stApp {
        background: linear-gradient(135deg, #0F0C29 0%, #1A1A2E 50%, #16213E 100%);
        color: #E8E8E8;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213E 0%, #0F0C29 100%);
        border-right: 1px solid rgba(108, 99, 255, 0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(22, 33, 62, 0.9), rgba(15, 12, 41, 0.9));
        border: 1px solid rgba(108, 99, 255, 0.3);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(108, 99, 255, 0.2);
    }
    .metric-value {
        font-size: 2rem; font-weight: 800;
        background: linear-gradient(135deg, #6C63FF, #00D2FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 8px 0;
    }
    .metric-value-ghs {
        font-size: 2rem; font-weight: 800;
        background: linear-gradient(135deg, #FFB300, #FF6584);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 8px 0;
    }
    .metric-label {
        font-size: 0.85rem; color: #8892B0; text-transform: uppercase;
        letter-spacing: 1.5px; font-weight: 600;
    }
    .metric-delta { font-size: 0.9rem; font-weight: 600; margin-top: 4px; }
    .delta-positive { color: #00C853; }
    .delta-negative { color: #FF6584; }
    .dashboard-title {
        font-size: 2.4rem; font-weight: 800;
        background: linear-gradient(135deg, #6C63FF, #00D2FF, #FF6584);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0; letter-spacing: -0.5px;
    }
    .dashboard-subtitle {
        text-align: center; color: #8892B0; font-size: 1rem;
        margin-top: 4px; margin-bottom: 30px; letter-spacing: 2px; text-transform: uppercase;
    }
    .section-header {
        font-size: 1.3rem; font-weight: 700; color: #E8E8E8;
        margin: 30px 0 15px 0; padding-bottom: 8px;
        border-bottom: 2px solid rgba(108, 99, 255, 0.3);
    }
    .channel-banner {
        background: linear-gradient(135deg, rgba(22, 33, 62, 0.95), rgba(15, 12, 41, 0.95));
        border: 1px solid rgba(108, 99, 255, 0.3);
        border-radius: 16px; padding: 30px; margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .channel-name {
        font-size: 1.8rem; font-weight: 800;
        background: linear-gradient(135deg, #6C63FF, #00D2FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .channel-desc { color: #8892B0; font-size: 0.95rem; margin-top: 8px; line-height: 1.5; }
    .channel-tag {
        display: inline-block; padding: 4px 12px; border-radius: 8px;
        font-size: 0.75rem; font-weight: 700; letter-spacing: 1px; margin-right: 8px;
    }
    .tag-ghs { background: rgba(255,179,0,0.2); color: #FFB300; }
    .tag-usd { background: rgba(0,210,255,0.2); color: #00D2FF; }
    .tag-source { background: rgba(108,99,255,0.2); color: #6C63FF; }
    div[data-testid="stExpander"] { border: 1px solid rgba(108,99,255,0.2); border-radius: 12px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "seevcash_compiled_data.csv")
    df = pd.read_csv(path, parse_dates=["month"])
    return df.sort_values("month").reset_index(drop=True)


def fmt_currency(val, symbol="$"):
    if abs(val) >= 1_000_000:
        return f"{symbol}{val/1_000_000:,.1f}M"
    if abs(val) >= 1_000:
        return f"{symbol}{val/1_000:,.1f}K"
    return f"{symbol}{val:,.0f}"


def fmt_number(val):
    if abs(val) >= 1_000_000:
        return f"{val/1_000_000:,.1f}M"
    if abs(val) >= 1_000:
        return f"{val/1_000:,.1f}K"
    return f"{val:,.0f}"


def pct_change(new, old):
    return (new - old) / old * 100 if old > 0 else 0


def chart_layout(title="", height=420):
    return dict(
        title=dict(text=title, font=dict(size=16, color=COLORS["text"], family="Inter"), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=COLORS["text"], size=12),
        height=height, margin=dict(l=50, r=30, t=60, b=50),
        xaxis=dict(gridcolor=COLORS["grid"], showline=True, linecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor=COLORS["grid"], showline=True, linecolor="rgba(255,255,255,0.1)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        hovermode="x unified",
    )


def add_projections(df, col, months_ahead=6):
    df_valid = df[df["month"] < "2026-03-01"].copy()
    recent = df_valid.tail(6)
    if len(recent) < 2:
        return pd.DataFrame(columns=["month", col])
    x = np.arange(len(recent))
    fit = np.polyfit(x, recent[col].values, 1)
    last_month = recent["month"].iloc[-1]
    proj_months = pd.date_range(last_month + pd.DateOffset(months=1), periods=months_ahead, freq="MS")
    proj_x = np.arange(len(recent), len(recent) + months_ahead)
    proj_vals = np.maximum(fit[0] * proj_x + fit[1], 0)
    return pd.DataFrame({"month": proj_months, col: proj_vals})


def delta_html(val, suffix="%"):
    cls = "delta-positive" if val >= 0 else "delta-negative"
    arr = "▲" if val >= 0 else "▼"
    return f'<span class="metric-delta {cls}">{arr} {abs(val):.1f}{suffix}</span>'


# ============================================================
#  DEEP DIVE VIEW
# ============================================================
def render_deep_dive(df_f, df_full, channel_name):
    meta = CHANNEL_META[channel_name]
    prefix = meta["prefix"]
    cur = meta["currency"]
    sym = "GH₵" if cur == "GHS" else "$"
    color = CHANNEL_COLORS[channel_name]
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    fill_light = f"rgba({r},{g},{b},0.12)"
    fill_med = f"rgba({r},{g},{b},0.15)"

    vol_col = f"{prefix}_ghs" if cur == "GHS" else f"{prefix}_usd"
    fee_col = f"{prefix}_fees_ghs" if cur == "GHS" else f"{prefix}_fees_usd"
    cnt_col = f"{prefix}_count"
    has_vol = vol_col in df_f.columns
    has_fees = meta["has_fees"] and fee_col in df_f.columns
    has_count = meta["has_count"] and cnt_col in df_f.columns

    if not has_vol:
        st.warning(f"No volume data found for {channel_name}.")
        return

    vol = df_f[vol_col]
    active = df_f[vol > 0]

    tag_cur = f'<span class="channel-tag tag-{cur.lower()}">{cur}</span>'
    tag_src = f'<span class="channel-tag tag-source">{meta["source"]}</span>'

    st.markdown(f"""
    <div class="channel-banner">
        <div class="channel-name">{channel_name}</div>
        <div style="margin-top:10px;">{tag_cur}{tag_src}</div>
        <div class="channel-desc">{meta['description']}</div>
    </div>""", unsafe_allow_html=True)

    # --- KPI cards ---
    total_vol = vol.sum()
    total_fees = df_f[fee_col].sum() if has_fees else 0
    total_count = int(df_f[cnt_col].sum()) if has_count else 0
    active_months = len(active)
    avg_monthly = total_vol / active_months if active_months > 0 else 0
    peak_vol = vol.max()
    peak_month = df_f.loc[vol.idxmax(), "month_label"] if peak_vol > 0 else "—"

    avg_txn_size = total_vol / total_count if total_count > 0 else 0
    fee_rate = (total_fees / total_vol * 100) if total_vol > 0 and has_fees else 0

    latest_vol = vol.iloc[-1]
    prev_vol = vol.iloc[-2] if len(vol) > 1 else 0
    vol_growth = pct_change(latest_vol, prev_vol) if prev_vol > 0 else 0

    ncols = 4 if has_count else 3
    cols = st.columns(ncols + 2)

    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Volume</div>
            <div class="metric-value" style="font-size:1.7rem;">{fmt_currency(total_vol, sym)}</div>
            <div class="metric-delta" style="color:#8892B0;">{active_months} active months</div>
        </div>""", unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Peak Month</div>
            <div class="metric-value" style="font-size:1.7rem;">{fmt_currency(peak_vol, sym)}</div>
            <div class="metric-delta" style="color:#8892B0;">{peak_month}</div>
        </div>""", unsafe_allow_html=True)

    with cols[2]:
        d = delta_html(vol_growth)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Latest Month</div>
            <div class="metric-value" style="font-size:1.7rem;">{fmt_currency(latest_vol, sym)}</div>
            {d}
        </div>""", unsafe_allow_html=True)

    if has_count:
        with cols[3]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Transactions</div>
                <div class="metric-value" style="font-size:1.7rem;">{fmt_number(total_count)}</div>
                <div class="metric-delta" style="color:#8892B0;">Avg size: {fmt_currency(avg_txn_size, sym)}</div>
            </div>""", unsafe_allow_html=True)

    fee_idx = ncols
    with cols[fee_idx]:
        if has_fees:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Fees</div>
                <div class="metric-value" style="font-size:1.7rem;">{fmt_currency(total_fees, sym)}</div>
                <div class="metric-delta" style="color:#8892B0;">Rate: {fee_rate:.2f}%</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Monthly</div>
                <div class="metric-value" style="font-size:1.7rem;">{fmt_currency(avg_monthly, sym)}</div>
                <div class="metric-delta" style="color:#8892B0;">over {active_months} months</div>
            </div>""", unsafe_allow_html=True)

    with cols[fee_idx + 1]:
        if cur == "GHS":
            usd_col = f"{prefix}_usd"
            usd_total = df_f[usd_col].sum() if usd_col in df_f.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">USD Equivalent</div>
                <div class="metric-value" style="font-size:1.7rem;">{fmt_currency(usd_total)}</div>
                <div class="metric-delta" style="color:#8892B0;">converted</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Monthly</div>
                <div class="metric-value" style="font-size:1.7rem;">{fmt_currency(avg_monthly, sym)}</div>
                <div class="metric-delta" style="color:#8892B0;">over {active_months} months</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 1. Volume trend ---
    st.markdown(f'<div class="section-header">{channel_name} — Volume Trend ({cur})</div>', unsafe_allow_html=True)

    fig_v = go.Figure()
    fig_v.add_trace(go.Bar(
        x=df_f["month"], y=vol,
        name="Monthly Volume",
        marker=dict(color=vol, colorscale=[[0, f"rgba({r},{g},{b},0.4)"], [1, color]], cornerradius=5),
        hovertemplate="<b>%{x|%b %Y}</b><br>" + f"{sym}" + "%{y:,.0f}<extra></extra>",
    ))
    fig_v.add_trace(go.Scatter(
        x=df_f["month"], y=vol,
        mode="lines+markers", name="Trend",
        line=dict(color="white", width=2), marker=dict(size=5, color="white"),
        hoverinfo="skip",
    ))
    if len(active) >= 3:
        proj = add_projections(df_full, vol_col, 6)
        if not proj.empty:
            fig_v.add_trace(go.Scatter(
                x=pd.concat([df_f["month"].iloc[-1:], proj["month"]]),
                y=pd.concat([vol.iloc[-1:], proj[vol_col]]),
                mode="lines+markers", name="Projected",
                line=dict(color=COLORS["secondary"], width=2.5, dash="dash"),
                marker=dict(size=6, symbol="diamond", color=COLORS["secondary"]),
            ))
    fig_v.update_layout(**chart_layout(f"Monthly Volume ({cur})", 420))
    fig_v.update_yaxes(title_text=f"Volume ({sym})")
    st.plotly_chart(fig_v, use_container_width=True)

    # --- 2. Count + Fees side by side ---
    if has_count or has_fees:
        c1, c2 = st.columns(2)

        if has_count:
            with c1:
                cnt = df_f[cnt_col]
                fig_c = go.Figure()
                fig_c.add_trace(go.Bar(
                    x=df_f["month"], y=cnt, name="Transactions",
                    marker=dict(color=cnt, colorscale=[[0, "#6C63FF"], [1, "#00C853"]], cornerradius=5),
                    hovertemplate="<b>%{x|%b %Y}</b><br>Count: %{y:,.0f}<extra></extra>",
                ))
                fig_c.update_layout(**chart_layout("Transaction Count", 380))
                fig_c.update_yaxes(title_text="Count")
                st.plotly_chart(fig_c, use_container_width=True)

        if has_fees:
            target = c2 if has_count else c1
            with target:
                fees = df_f[fee_col]
                fig_fee = go.Figure()
                fig_fee.add_trace(go.Bar(
                    x=df_f["month"], y=fees, name="Fees",
                    marker=dict(color=fees, colorscale=[[0, "#FF6584"], [1, "#FFB300"]], cornerradius=5),
                    hovertemplate="<b>%{x|%b %Y}</b><br>" + f"Fee: {sym}" + "%{y:,.2f}<extra></extra>",
                ))
                fig_fee.update_layout(**chart_layout(f"Fee Revenue ({cur})", 380))
                fig_fee.update_yaxes(title_text=f"Fees ({sym})")
                st.plotly_chart(fig_fee, use_container_width=True)

    # --- 3. Avg transaction size + Fee rate ---
    if has_count and has_fees:
        st.markdown(f'<div class="section-header">Efficiency Metrics</div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)

        with c3:
            avg_size = vol / df_f[cnt_col].replace(0, np.nan)
            fig_avg = go.Figure()
            fig_avg.add_trace(go.Scatter(
                x=df_f["month"], y=avg_size,
                mode="lines+markers", name="Avg Txn Size",
                line=dict(color=COLORS["secondary"], width=3),
                marker=dict(size=7),
                fill="tozeroy", fillcolor="rgba(0,210,255,0.1)",
                hovertemplate="<b>%{x|%b %Y}</b><br>" + f"Avg: {sym}" + "%{y:,.2f}<extra></extra>",
            ))
            fig_avg.update_layout(**chart_layout(f"Average Transaction Size ({cur})", 380))
            fig_avg.update_yaxes(title_text=f"Avg Size ({sym})")
            st.plotly_chart(fig_avg, use_container_width=True)

        with c4:
            fee_pct = df_f[fee_col] / vol.replace(0, np.nan) * 100
            fig_rate = go.Figure()
            fig_rate.add_trace(go.Scatter(
                x=df_f["month"], y=fee_pct,
                mode="lines+markers", name="Fee Rate",
                line=dict(color=COLORS["accent"], width=3),
                marker=dict(size=7),
                fill="tozeroy", fillcolor="rgba(255,101,132,0.1)",
                hovertemplate="<b>%{x|%b %Y}</b><br>Rate: %{y:.2f}%<extra></extra>",
            ))
            fig_rate.update_layout(**chart_layout("Fee Rate (% of Volume)", 380))
            fig_rate.update_yaxes(title_text="Fee Rate (%)")
            st.plotly_chart(fig_rate, use_container_width=True)

    elif has_count:
        st.markdown(f'<div class="section-header">Average Transaction Size</div>', unsafe_allow_html=True)
        avg_size = vol / df_f[cnt_col].replace(0, np.nan)
        fig_avg = go.Figure()
        fig_avg.add_trace(go.Scatter(
            x=df_f["month"], y=avg_size,
            mode="lines+markers", name="Avg Txn Size",
            line=dict(color=COLORS["secondary"], width=3), marker=dict(size=7),
            fill="tozeroy", fillcolor="rgba(0,210,255,0.1)",
            hovertemplate="<b>%{x|%b %Y}</b><br>" + f"Avg: {sym}" + "%{y:,.2f}<extra></extra>",
        ))
        fig_avg.update_layout(**chart_layout(f"Average Transaction Size ({cur})", 380))
        fig_avg.update_yaxes(title_text=f"Avg Size ({sym})")
        st.plotly_chart(fig_avg, use_container_width=True)

    # --- 4. MoM Growth ---
    st.markdown(f'<div class="section-header">Month-on-Month Growth</div>', unsafe_allow_html=True)

    df_g = df_f.copy()
    df_g["vol_g"] = vol.pct_change() * 100
    if has_count:
        df_g["cnt_g"] = df_f[cnt_col].pct_change() * 100
    df_g = df_g.iloc[1:]

    fig_g = go.Figure()
    fig_g.add_trace(go.Bar(
        x=df_g["month"], y=df_g["vol_g"], name="Volume Growth",
        marker=dict(
            color=[COLORS["success"] if v >= 0 else COLORS["accent"] for v in df_g["vol_g"]],
            cornerradius=4,
        ),
        hovertemplate="<b>%{x|%b %Y}</b><br>Volume: %{y:+.1f}%<extra></extra>",
    ))
    if has_count:
        fig_g.add_trace(go.Scatter(
            x=df_g["month"], y=df_g["cnt_g"],
            mode="lines+markers", name="Count Growth",
            line=dict(color=COLORS["warning"], width=2.5), marker=dict(size=6),
            hovertemplate="<b>%{x|%b %Y}</b><br>Count: %{y:+.1f}%<extra></extra>",
        ))
    fig_g.add_hline(y=0, line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dash"))
    fig_g.update_layout(**chart_layout("MoM Growth Rate (%)", 400))
    fig_g.update_yaxes(title_text="Growth (%)")
    st.plotly_chart(fig_g, use_container_width=True)

    # --- 5. Cumulative ---
    st.markdown(f'<div class="section-header">Cumulative Volume</div>', unsafe_allow_html=True)

    cum = vol.cumsum()
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=df_f["month"], y=cum,
        mode="lines+markers", name="Cumulative",
        line=dict(color=color, width=3), marker=dict(size=6),
        fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.12)",
        hovertemplate="<b>%{x|%b %Y}</b><br>" + f"Cum: {sym}" + "%{y:,.0f}<extra></extra>",
    ))
    fig_cum.update_layout(**chart_layout(f"Cumulative Volume ({cur})", 380))
    fig_cum.update_yaxes(title_text=f"Cumulative ({sym})")
    st.plotly_chart(fig_cum, use_container_width=True)

    # --- 6. Share of total (within same currency) ---
    st.markdown(f'<div class="section-header">Share of {cur} Total</div>', unsafe_allow_html=True)

    if cur == "GHS":
        total_col = "total_volume_ghs"
    else:
        total_col = "total_volume_usd"
    share = vol / df_f[total_col].replace(0, np.nan) * 100
    fig_share = go.Figure()
    fig_share.add_trace(go.Scatter(
        x=df_f["month"], y=share,
        mode="lines+markers", name="% of Total",
        line=dict(color=color, width=3), marker=dict(size=7),
        fill="tozeroy", fillcolor=fill_med,
        hovertemplate="<b>%{x|%b %Y}</b><br>Share: %{y:.1f}%<extra></extra>",
    ))
    fig_share.update_layout(**chart_layout(f"{channel_name} as % of Total {cur} Volume", 350))
    fig_share.update_yaxes(title_text="Share (%)")
    st.plotly_chart(fig_share, use_container_width=True)

    # --- 7. Data table ---
    st.markdown(f'<div class="section-header">Raw Data — {channel_name}</div>', unsafe_allow_html=True)

    table_cols = {"Month": df_f["month_label"]}
    table_cols[f"Volume ({cur})"] = vol.apply(lambda x: f"{sym}{x:,.2f}")
    if has_count:
        table_cols["Transactions"] = df_f[cnt_col].apply(lambda x: f"{int(x):,}")
    if has_fees:
        table_cols[f"Fees ({cur})"] = df_f[fee_col].apply(lambda x: f"{sym}{x:,.2f}")
    if has_count and vol.sum() > 0:
        avg_s = vol / df_f[cnt_col].replace(0, np.nan)
        table_cols[f"Avg Size ({cur})"] = avg_s.apply(lambda x: f"{sym}{x:,.2f}" if pd.notna(x) else "—")
    if has_fees and vol.sum() > 0:
        fr = df_f[fee_col] / vol.replace(0, np.nan) * 100
        table_cols["Fee Rate"] = fr.apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "—")

    tbl = pd.DataFrame(table_cols)
    st.dataframe(tbl, use_container_width=True, hide_index=True)


# ============================================================
#  OVERVIEW VIEW
# ============================================================
def render_overview(df_filtered, df_full, selected_channels, proj_months):
    latest = df_filtered.iloc[-1]
    prev = df_filtered.iloc[-2] if len(df_filtered) > 1 else latest

    ghs_delta = pct_change(latest["total_volume_ghs"], prev["total_volume_ghs"])
    usd_delta = pct_change(latest["total_volume_usd"], prev["total_volume_usd"])
    cnt_delta = pct_change(latest["total_transaction_count"], prev["total_transaction_count"])

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        d_cls = "delta-positive" if ghs_delta >= 0 else "delta-negative"
        d_arr = "▲" if ghs_delta >= 0 else "▼"
        st.markdown(f"""<div class="metric-card"><div class="metric-label">GHS Volume (9 channels)</div>
        <div class="metric-value-ghs">{fmt_currency(latest['total_volume_ghs'], 'GH₵')}</div>
        <div class="metric-delta {d_cls}">{d_arr} {abs(ghs_delta):.1f}% MoM</div></div>""", unsafe_allow_html=True)
    with kpi2:
        d_cls = "delta-positive" if usd_delta >= 0 else "delta-negative"
        d_arr = "▲" if usd_delta >= 0 else "▼"
        st.markdown(f"""<div class="metric-card"><div class="metric-label">USD Volume (On-chain)</div>
        <div class="metric-value">{fmt_currency(latest['total_volume_usd'])}</div>
        <div class="metric-delta {d_cls}">{d_arr} {abs(usd_delta):.1f}% MoM</div></div>""", unsafe_allow_html=True)
    with kpi3:
        d_cls = "delta-positive" if cnt_delta >= 0 else "delta-negative"
        d_arr = "▲" if cnt_delta >= 0 else "▼"
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Monthly Transactions</div>
        <div class="metric-value">{fmt_number(latest['total_transaction_count'])}</div>
        <div class="metric-delta {d_cls}">{d_arr} {abs(cnt_delta):.1f}% MoM</div></div>""", unsafe_allow_html=True)
    with kpi4:
        cum_ghs = df_filtered["total_volume_ghs"].sum()
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Cumulative GHS</div>
        <div class="metric-value-ghs">{fmt_currency(cum_ghs, 'GH₵')}</div>
        <div class="metric-delta" style="color:#8892B0;">{len(df_filtered)} months</div></div>""", unsafe_allow_html=True)
    with kpi5:
        cum_usd = df_filtered["total_volume_usd"].sum()
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Cumulative USD</div>
        <div class="metric-value">{fmt_currency(cum_usd)}</div>
        <div class="metric-delta" style="color:#8892B0;">On-chain only</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # GHS and USD volume trends (separate, not blended)
    st.markdown('<div class="section-header">Volume Trends & Projections</div>', unsafe_allow_html=True)
    v1, v2 = st.columns(2)
    with v1:
        proj_ghs = add_projections(df_full, "total_volume_ghs", proj_months)
        fig_gv = go.Figure()
        fig_gv.add_trace(go.Scatter(x=df_full["month"], y=df_full["total_volume_ghs"],
            mode="lines+markers", name="Actual",
            line=dict(color=COLORS["ghs"], width=3),
            marker=dict(size=7, color=COLORS["ghs"]),
            fill="tozeroy", fillcolor="rgba(255,179,0,0.1)",
            hovertemplate="<b>%{x|%b %Y}</b><br>GH₵%{y:,.0f}<extra></extra>"))
        if not proj_ghs.empty:
            fig_gv.add_trace(go.Scatter(
                x=pd.concat([df_full["month"].iloc[-1:], proj_ghs["month"]]),
                y=pd.concat([df_full["total_volume_ghs"].iloc[-1:], proj_ghs["total_volume_ghs"]]),
                mode="lines+markers", name="Projected",
                line=dict(color="#FF6584", width=2.5, dash="dash"),
                marker=dict(size=6, symbol="diamond")))
        fig_gv.update_layout(**chart_layout("GHS Volume — 9 Local Channels", 420))
        fig_gv.update_yaxes(title_text="Volume (GH₵)")
        st.plotly_chart(fig_gv, use_container_width=True)
    with v2:
        proj_usd = add_projections(df_full, "total_volume_usd", proj_months)
        fig_uv = go.Figure()
        fig_uv.add_trace(go.Scatter(x=df_full["month"], y=df_full["total_volume_usd"],
            mode="lines+markers", name="Actual",
            line=dict(color=COLORS["usd"], width=3),
            marker=dict(size=7, color=COLORS["usd"]),
            fill="tozeroy", fillcolor="rgba(0,210,255,0.1)",
            hovertemplate="<b>%{x|%b %Y}</b><br>$%{y:,.0f}<extra></extra>"))
        if not proj_usd.empty:
            fig_uv.add_trace(go.Scatter(
                x=pd.concat([df_full["month"].iloc[-1:], proj_usd["month"]]),
                y=pd.concat([df_full["total_volume_usd"].iloc[-1:], proj_usd["total_volume_usd"]]),
                mode="lines+markers", name="Projected",
                line=dict(color=COLORS["success"], width=2.5, dash="dash"),
                marker=dict(size=6, symbol="diamond")))
        fig_uv.update_layout(**chart_layout("USD Volume — On-chain (Deposit + Withdraw)", 420))
        fig_uv.update_yaxes(title_text="Volume ($)")
        st.plotly_chart(fig_uv, use_container_width=True)

    # Count + Fees
    ca, cb = st.columns(2)
    with ca:
        fig_cnt = go.Figure()
        fig_cnt.add_trace(go.Bar(x=df_filtered["month"], y=df_filtered["total_transaction_count"],
            marker=dict(color=df_filtered["total_transaction_count"],
            colorscale=[[0,"#6C63FF"],[0.5,"#00D2FF"],[1,"#00C853"]], cornerradius=5),
            hovertemplate="<b>%{x|%b %Y}</b><br>Txns: %{y:,.0f}<extra></extra>"))
        fig_cnt.update_layout(**chart_layout("Monthly Transaction Count", 400))
        st.plotly_chart(fig_cnt, use_container_width=True)
    with cb:
        fig_fe = go.Figure()
        fig_fe.add_trace(go.Bar(x=df_filtered["month"], y=df_filtered["total_fees_ghs"],
            name="GHS Fees",
            marker=dict(color=COLORS["ghs"], cornerradius=5),
            hovertemplate="<b>%{x|%b %Y}</b><br>GHS Fees: GH₵%{y:,.2f}<extra></extra>"))
        fig_fe.add_trace(go.Bar(x=df_filtered["month"], y=df_filtered["total_fees_usd"],
            name="USD Fees",
            marker=dict(color=COLORS["usd"], cornerradius=5),
            hovertemplate="<b>%{x|%b %Y}</b><br>USD Fees: $%{y:,.2f}<extra></extra>"))
        lay = chart_layout("Monthly Fee Revenue", 400); lay["barmode"] = "group"
        fig_fe.update_layout(**lay)
        st.plotly_chart(fig_fe, use_container_width=True)

    # MoM growth (GHS-based since it's the dominant volume)
    st.markdown('<div class="section-header">Month-on-Month Growth Analysis</div>', unsafe_allow_html=True)
    dg = df_filtered.copy()
    dg["ghs_g"] = dg["total_volume_ghs"].pct_change() * 100
    dg["cnt_g"] = dg["total_transaction_count"].pct_change() * 100
    dg = dg.iloc[1:]
    fig_gr = go.Figure()
    fig_gr.add_trace(go.Bar(x=dg["month"], y=dg["ghs_g"], name="GHS Volume Growth",
        marker=dict(color=[COLORS["success"] if v>=0 else COLORS["accent"] for v in dg["ghs_g"]], cornerradius=4),
        hovertemplate="<b>%{x|%b %Y}</b><br>GHS Vol: %{y:+.1f}%<extra></extra>"))
    fig_gr.add_trace(go.Scatter(x=dg["month"], y=dg["cnt_g"], mode="lines+markers", name="Txn Count Growth",
        line=dict(color=COLORS["warning"], width=2.5), marker=dict(size=7),
        hovertemplate="<b>%{x|%b %Y}</b><br>Count: %{y:+.1f}%<extra></extra>"))
    fig_gr.add_hline(y=0, line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dash"))
    fig_gr.update_layout(**chart_layout("Month-on-Month Growth Rate (%)", 420))
    st.plotly_chart(fig_gr, use_container_width=True)

    # YoY
    st.markdown('<div class="section-header">Year-over-Year Comparison: 2025 vs 2026</div>', unsafe_allow_html=True)
    d25 = df_full[df_full["year"]==2025]; d26 = df_full[df_full["year"]==2026]
    cm = sorted(set(d25["month_num"]) & set(d26["month_num"]))
    mnames = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
    if cm:
        yoy = []
        for m in cm:
            r25 = d25[d25["month_num"]==m].iloc[0]; r26 = d26[d26["month_num"]==m].iloc[0]
            yoy.append({"month":mnames.get(m),
                "g25":r25["total_volume_ghs"],"g26":r26["total_volume_ghs"],
                "u25":r25["total_volume_usd"],"u26":r26["total_volume_usd"],
                "c25":r25["total_transaction_count"],"c26":r26["total_transaction_count"],
                "gg":pct_change(r26["total_volume_ghs"],r25["total_volume_ghs"]),
                "ug":pct_change(r26["total_volume_usd"],r25["total_volume_usd"]),
                "cg":pct_change(r26["total_transaction_count"],r25["total_transaction_count"])})
        ydf = pd.DataFrame(yoy)
        y1,y2 = st.columns(2)
        with y1:
            fg = go.Figure()
            fg.add_trace(go.Bar(x=ydf["month"],y=ydf["g25"],name="2025",marker=dict(color="rgba(255,179,0,0.5)",cornerradius=5),
                text=[fmt_currency(v,"GH₵") for v in ydf["g25"]],textposition="outside"))
            fg.add_trace(go.Bar(x=ydf["month"],y=ydf["g26"],name="2026",marker=dict(color=COLORS["ghs"],cornerradius=5),
                text=[fmt_currency(v,"GH₵") for v in ydf["g26"]],textposition="outside"))
            lay=chart_layout("GHS Volume — YoY",400);lay["barmode"]="group"
            fg.update_layout(**lay);st.plotly_chart(fg,use_container_width=True)
        with y2:
            fc = go.Figure()
            fc.add_trace(go.Bar(x=ydf["month"],y=ydf["c25"],name="2025",marker=dict(color="rgba(108,99,255,0.6)",cornerradius=5),
                text=[fmt_number(v) for v in ydf["c25"]],textposition="outside"))
            fc.add_trace(go.Bar(x=ydf["month"],y=ydf["c26"],name="2026",marker=dict(color=COLORS["secondary"],cornerradius=5),
                text=[fmt_number(v) for v in ydf["c26"]],textposition="outside"))
            lay=chart_layout("Txn Count — YoY",400);lay["barmode"]="group"
            fc.update_layout(**lay);st.plotly_chart(fc,use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        yc = st.columns(len(yoy))
        for i,row in enumerate(yoy):
            with yc[i]:
                st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{row['month']} YoY</div>
                <div class="metric-value-ghs" style="font-size:1.6rem;">{'+' if row['gg']>=0 else ''}{row['gg']:,.0f}%</div>
                <div class="metric-delta" style="color:#FFB300;">GHS Volume</div>
                <div style="color:#00C853;font-size:1rem;font-weight:700;margin-top:6px;">{'+' if row['cg']>=0 else ''}{row['cg']:,.0f}%</div>
                <div class="metric-delta" style="color:#8892B0;">Txn Count</div></div>""", unsafe_allow_html=True)

    # Channel breakdown
    st.markdown('<div class="section-header">Transaction Channel Breakdown</div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("**<span class='channel-tag tag-ghs'>GHS</span> Local Channels**", unsafe_allow_html=True)
        fig_gc = go.Figure()
        for nm, px in GHS_CHANNELS.items():
            if nm not in selected_channels: continue
            cn = f"{px}_ghs"
            if cn not in df_filtered.columns: continue
            c=CHANNEL_COLORS[nm]; ri,gi,bi=int(c[1:3],16),int(c[3:5],16),int(c[5:7],16)
            fig_gc.add_trace(go.Scatter(x=df_filtered["month"],y=df_filtered[cn],mode="lines",name=nm,stackgroup="one",
                line=dict(width=0.5,color=c),fillcolor=f"rgba({ri},{gi},{bi},0.6)",
                hovertemplate=f"<b>{nm}</b><br>"+"%{x|%b %Y}: GH₵%{y:,.0f}<extra></extra>"))
        fig_gc.update_layout(**chart_layout("GHS Channels (Stacked)",420))
        st.plotly_chart(fig_gc,use_container_width=True)
    with ch2:
        st.markdown("**<span class='channel-tag tag-usd'>USD</span> Digital Channels**", unsafe_allow_html=True)
        fig_uc = go.Figure()
        for nm, px in USD_CHANNELS.items():
            if nm not in selected_channels: continue
            cn = f"{px}_usd"
            if cn not in df_filtered.columns: continue
            c=CHANNEL_COLORS[nm]; ri,gi,bi=int(c[1:3],16),int(c[3:5],16),int(c[5:7],16)
            fig_uc.add_trace(go.Scatter(x=df_filtered["month"],y=df_filtered[cn],mode="lines",name=nm,stackgroup="one",
                line=dict(width=0.5,color=c),fillcolor=f"rgba({ri},{gi},{bi},0.6)",
                hovertemplate=f"<b>{nm}</b><br>"+"%{x|%b %Y}: $%{y:,.0f}<extra></extra>"))
        fig_uc.update_layout(**chart_layout("USD Channels (Stacked)",420))
        st.plotly_chart(fig_uc,use_container_width=True)

    # Market share (GHS channels — since 9 of 11 channels are GHS)
    cp, cbar = st.columns(2)
    with cp:
        pd_data = []
        for nm,px in GHS_CHANNELS.items():
            if nm not in selected_channels: continue
            cn=f"{px}_ghs"
            if cn in df_filtered.columns:
                t=df_filtered[cn].sum()
                if t>0: pd_data.append({"channel":nm,"volume":t})
        pdf = pd.DataFrame(pd_data).sort_values("volume",ascending=False) if pd_data else pd.DataFrame()
        if not pdf.empty:
            fp = go.Figure(go.Pie(labels=pdf["channel"],values=pdf["volume"],hole=0.55,
                marker=dict(colors=[CHANNEL_COLORS[n] for n in pdf["channel"]]),
                textinfo="label+percent",textfont=dict(size=10),
                hovertemplate="<b>%{label}</b><br>GH₵%{value:,.0f}<extra></extra>"))
            fp.update_layout(**chart_layout("GHS Channel Market Share",420))
            st.plotly_chart(fp,use_container_width=True)
    with cbar:
        if not pdf.empty:
            bd = pdf.head(9)
            fb = go.Figure(go.Bar(y=bd["channel"],x=bd["volume"],orientation="h",
                marker=dict(color=[CHANNEL_COLORS[n] for n in bd["channel"]],cornerradius=5),
                text=[fmt_currency(v,"GH₵") for v in bd["volume"]],textposition="outside"))
            lay=chart_layout("Top GHS Channels by Volume",420);lay["yaxis"]["autorange"]="reversed"
            fb.update_layout(**lay);st.plotly_chart(fb,use_container_width=True)

    # On-chain
    st.markdown('<div class="section-header">On-chain (Crypto) Activity — USD</div>', unsafe_allow_html=True)
    o1,o2 = st.columns(2)
    with o1:
        fo = go.Figure()
        fo.add_trace(go.Bar(x=df_filtered["month"],y=df_filtered["onchain_deposit_usd"],name="Deposits",marker=dict(color=COLORS["success"],cornerradius=4)))
        fo.add_trace(go.Bar(x=df_filtered["month"],y=df_filtered["onchain_withdraw_usd"],name="Withdrawals",marker=dict(color=COLORS["accent"],cornerradius=4)))
        lay=chart_layout("Deposits vs Withdrawals",380);lay["barmode"]="group"
        fo.update_layout(**lay);st.plotly_chart(fo,use_container_width=True)
    with o2:
        net=df_filtered["onchain_deposit_usd"]-df_filtered["onchain_withdraw_usd"]
        fn = go.Figure(go.Bar(x=df_filtered["month"],y=net,
            marker=dict(color=[COLORS["success"] if v>=0 else COLORS["accent"] for v in net],cornerradius=4)))
        fn.add_hline(y=0,line=dict(color="rgba(255,255,255,0.3)",width=1))
        fn.update_layout(**chart_layout("Net On-chain Flow",380))
        st.plotly_chart(fn,use_container_width=True)

    # Projections
    st.markdown('<div class="section-header">Revenue & Growth Projections</div>', unsafe_allow_html=True)
    pf = add_projections(df_full,"total_fees_usd",proj_months)
    pc = add_projections(df_full,"total_transaction_count",proj_months)
    p1,p2 = st.columns(2)
    with p1:
        ffp = go.Figure()
        ffp.add_trace(go.Scatter(x=df_full["month"],y=df_full["total_fees_usd"],mode="lines+markers",name="Actual",
            line=dict(color=COLORS["accent"],width=3),fill="tozeroy",fillcolor="rgba(255,101,132,0.1)"))
        if not pf.empty:
            ffp.add_trace(go.Scatter(x=pd.concat([df_full["month"].iloc[-1:],pf["month"]]),
                y=pd.concat([df_full["total_fees_usd"].iloc[-1:],pf["total_fees_usd"]]),
                mode="lines+markers",name="Projected",line=dict(color=COLORS["warning"],width=3,dash="dash"),
                marker=dict(symbol="diamond")))
        ffp.update_layout(**chart_layout("Fee Revenue — Projected",400))
        st.plotly_chart(ffp,use_container_width=True)
    with p2:
        ftp = go.Figure()
        ftp.add_trace(go.Scatter(x=df_full["month"],y=df_full["total_transaction_count"],mode="lines+markers",name="Actual",
            line=dict(color=COLORS["secondary"],width=3),fill="tozeroy",fillcolor="rgba(0,210,255,0.1)"))
        if not pc.empty:
            ftp.add_trace(go.Scatter(x=pd.concat([df_full["month"].iloc[-1:],pc["month"]]),
                y=pd.concat([df_full["total_transaction_count"].iloc[-1:],pc["total_transaction_count"]]),
                mode="lines+markers",name="Projected",line=dict(color=COLORS["success"],width=3,dash="dash"),
                marker=dict(symbol="diamond")))
        ftp.update_layout(**chart_layout("Txn Count — Projected",400))
        st.plotly_chart(ftp,use_container_width=True)

    # Cumulative
    st.markdown('<div class="section-header">Cumulative Growth</div>', unsafe_allow_html=True)
    cm1, cm2 = st.columns(2)
    with cm1:
        dcm = df_filtered.copy()
        dcm["cv"]=dcm["total_volume_ghs"].cumsum()
        fcm = go.Figure()
        fcm.add_trace(go.Scatter(x=dcm["month"],y=dcm["cv"],mode="lines+markers",name="Cum GHS",
            line=dict(color=COLORS["ghs"],width=3),fill="tozeroy",fillcolor="rgba(255,179,0,0.08)"))
        fcm.update_layout(**chart_layout("Cumulative GHS Volume",380))
        fcm.update_yaxes(title_text="GH₵")
        st.plotly_chart(fcm,use_container_width=True)
    with cm2:
        dcm2 = df_filtered.copy()
        dcm2["cv"]=dcm2["total_volume_usd"].cumsum()
        fcm2 = go.Figure()
        fcm2.add_trace(go.Scatter(x=dcm2["month"],y=dcm2["cv"],mode="lines+markers",name="Cum USD",
            line=dict(color=COLORS["usd"],width=3),fill="tozeroy",fillcolor="rgba(0,210,255,0.08)"))
        fcm2.update_layout(**chart_layout("Cumulative USD Volume (On-chain)",380))
        fcm2.update_yaxes(title_text="$")
        st.plotly_chart(fcm2,use_container_width=True)

    # Data table
    st.markdown('<div class="section-header">Detailed Data Table</div>', unsafe_allow_html=True)
    dtbl = df_filtered[["month_label","total_volume_ghs","total_volume_usd",
                         "total_transaction_count","total_fees_ghs","total_fees_usd"]].copy()
    dtbl.columns = ["Month","GHS Volume (9 channels)","USD Volume (On-chain)","Total Txns","GHS Fees","USD Fees"]
    dtbl["GHS Volume (9 channels)"] = dtbl["GHS Volume (9 channels)"].apply(lambda x: f"GH₵{x:,.2f}")
    dtbl["USD Volume (On-chain)"] = dtbl["USD Volume (On-chain)"].apply(lambda x: f"${x:,.2f}")
    dtbl["Total Txns"] = dtbl["Total Txns"].apply(lambda x: f"{int(x):,}")
    dtbl["GHS Fees"] = dtbl["GHS Fees"].apply(lambda x: f"GH₵{x:,.2f}")
    dtbl["USD Fees"] = dtbl["USD Fees"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(dtbl, use_container_width=True, hide_index=True)


# ============================================================
#  MAIN
# ============================================================
df = load_data()
df_full = df[df["month"] < "2026-03-01"].copy()

st.markdown('<h1 class="dashboard-title">SeevCash Analytics</h1>', unsafe_allow_html=True)
st.markdown('<p class="dashboard-subtitle">Investor Intelligence Dashboard</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Dashboard View")
    active_view = st.radio("Select view:", ["Overview", "Channel Deep Dive"], index=0, horizontal=True)

    st.markdown("---")
    st.markdown("### Filters")
    date_range = st.select_slider("Date Range", options=df_full["month_label"].tolist(),
        value=(df_full["month_label"].iloc[0], df_full["month_label"].iloc[-1]))
    si = df_full[df_full["month_label"] == date_range[0]].index[0]
    ei = df_full[df_full["month_label"] == date_range[1]].index[0]
    df_filtered = df_full.iloc[si:ei + 1].copy()

    if active_view == "Channel Deep Dive":
        st.markdown("---")
        st.markdown("### Select Channel")
        deep_dive_channel = st.selectbox("Analyze:", options=list(CHANNEL_META.keys()), index=0)
    else:
        st.markdown("---")
        st.markdown("### Transaction Channels")
        selected_channels = st.multiselect("Select channels", options=list(ALL_CHANNELS.keys()),
            default=list(ALL_CHANNELS.keys()))
        st.markdown("---")
        proj_months = st.slider("Projection Months Ahead", 2, 12, 6)

    st.markdown("---")
    st.markdown("##### Exchange Rate")
    if len(df_filtered) > 0:
        st.markdown(f"**1 USD = {df_filtered['ghs_usd_rate'].iloc[-1]:.1f} GHS**")
    st.markdown("<div style='text-align:center;color:#8892B0;font-size:0.75rem;margin-top:20px;'>"
        "Data as of March 2026<br>SeevCash v3.0</div>", unsafe_allow_html=True)

if active_view == "Channel Deep Dive":
    render_deep_dive(df_filtered, df_full, deep_dive_channel)
else:
    render_overview(df_filtered, df_full, selected_channels, proj_months)

st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#8892B0;font-size:0.8rem;padding:20px 0;'>"
    "<b>Currency Note:</b> GHS channels converted to USD using monthly Bank of Ghana rates. "
    f"USD channels reported natively.<br>Last updated: {datetime.now().strftime('%B %d, %Y')}</div>",
    unsafe_allow_html=True)
