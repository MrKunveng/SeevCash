# SeevCash Analytics Dashboard

Investor intelligence dashboard for SeevCash — a Ghanaian fintech platform processing transactions across Mobile Money, bank transfers, P2P, cross-border remittances, and on-chain crypto.

## Live Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://seevcash.streamlit.app)

## Data Coverage

- **Period**: October 2024 — March 2026
- **GHS Channels (9)**: Pay to MoMo, Add from MoMo, Withdraw to MoMo, Mobile Requests, Pay to Banks, SeevPlus Withdrawals, SeevAPI Transactions, P2P Transfers, Cross-border
- **USD Channels (2)**: On-chain Deposits, On-chain Withdrawals (crypto — USDT/USDC)

## Features

- **Overview Dashboard**: KPIs, volume trends with projections, MoM growth, YoY comparisons, channel breakdowns, on-chain crypto activity
- **Channel Deep Dive**: Select any of the 11 channels for detailed analysis — volume trends, fees, average transaction size, fee rate, MoM growth, cumulative volume, market share
- **Currency Integrity**: GHS and USD volumes kept strictly separate — no misleading blended figures

## Run Locally

```bash
pip install -r requirements.txt
python compile_data.py
streamlit run dashboard.py
```

## Tech Stack

- Python, Pandas, Plotly, Streamlit
