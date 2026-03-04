import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GHS_USD_RATES = {
    '2024-10': 15.5, '2024-11': 15.6, '2024-12': 15.7,
    '2025-01': 15.8, '2025-02': 15.9, '2025-03': 16.0,
    '2025-04': 16.0, '2025-05': 16.1, '2025-06': 16.2,
    '2025-07': 16.3, '2025-08': 16.3, '2025-09': 16.4,
    '2025-10': 16.5, '2025-11': 16.5, '2025-12': 16.6,
    '2026-01': 16.7, '2026-02': 16.8, '2026-03': 16.9,
}

def get_rate(month_dt):
    key = month_dt.strftime('%Y-%m')
    return GHS_USD_RATES.get(key, 16.5)

def parse_amount(val):
    if pd.isna(val):
        return 0.0
    s = str(val).replace(',', '').replace('$', '').strip()
    try:
        return float(s)
    except ValueError:
        return 0.0

def parse_month(val):
    val = str(val).strip().strip('"')
    try:
        return pd.to_datetime(val, format='%B, %Y')
    except:
        return pd.NaT

def parse_week_to_month(val):
    val = str(val).strip().strip('"')
    start_date_str = val.split(' - ')[0].strip()
    try:
        dt = pd.to_datetime(start_date_str, format='%B %d, %Y')
        return dt.replace(day=1)
    except:
        return pd.NaT


# ================================================================
# ALL GHS CHANNELS (9 channels in Ghana Cedis)
# ================================================================

# 1. Payment Made to Mobile Money (GHS)
df = pd.read_csv(os.path.join(BASE_DIR, 'paytomomos.csv'))
df.columns = [c.strip() for c in df.columns]
pay_to_momo = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_month),
    'pay_to_momo_ghs': df['Sum of TransactionAmount'].apply(parse_amount),
    'pay_to_momo_fees_ghs': df['Sum of TransactionCost ($)'].apply(parse_amount),
    'pay_to_momo_count': df['Count'].apply(parse_amount).astype(int),
})

# 2. Adding Money from Mobile Money (GHS)
df = pd.read_csv(os.path.join(BASE_DIR, 'adding_money_from_momo.csv'))
df.columns = [c.strip() for c in df.columns]
add_from_momo = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_month),
    'add_from_momo_ghs': df['Sum of TransactionAmount'].apply(parse_amount),
    'add_from_momo_fees_ghs': df['Sum of TransactionCost ($)'].apply(parse_amount),
    'add_from_momo_count': df['Count'].apply(parse_amount).astype(int),
})

# 3. Total Withdrawal to Mobile Money (GHS)
df = pd.read_csv(os.path.join(BASE_DIR, 'withdrawmoneytomomos.csv'))
df.columns = [c.strip() for c in df.columns]
withdraw_to_momo = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_month),
    'withdraw_to_momo_ghs': df['Sum of TransactionAmount'].apply(parse_amount),
    'withdraw_to_momo_fees_ghs': df['Sum of TransactionCost ($)'].apply(parse_amount),
    'withdraw_to_momo_count': df['Count'].apply(parse_amount).astype(int),
})

# 4. Transaction on Users Request from Mobile Money (GHS)
df = pd.read_csv(os.path.join(BASE_DIR, 'transaction_from_request_mobile.csv'))
df.columns = [c.strip() for c in df.columns]
mobile_request = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_month),
    'mobile_request_ghs': df['Sum of TransactionAmount'].apply(parse_amount),
    'mobile_request_fees_ghs': df['Sum of TransactionCost ($)'].apply(parse_amount),
    'mobile_request_count': df['Count'].apply(parse_amount).astype(int),
})

# 5. Payment Made to Bank Accounts (GHS)
df = pd.read_csv(os.path.join(BASE_DIR, 'paytobanks.csv'))
df.columns = [c.strip() for c in df.columns]
pay_to_banks = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_month),
    'pay_to_banks_ghs': df['Sum of TransactionAmount'].apply(parse_amount),
    'pay_to_banks_fees_ghs': df['Sum of TransactionCost ($)'].apply(parse_amount),
    'pay_to_banks_count': df['Count'].apply(parse_amount).astype(int),
})

# 6. Transactions - SeevPlus Withdraw (GHS, weekly -> monthly)
df = pd.read_csv(os.path.join(BASE_DIR, 'transactions___seevplus_withdraw.csv'))
df.columns = [c.strip() for c in df.columns]
seevplus = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_week_to_month),
    'seevplus_withdraw_ghs': df['Sum of Amount'].apply(parse_amount),
    'seevplus_withdraw_fees_ghs': df['Sum of FeeAmount'].apply(parse_amount),
    'seevplus_withdraw_count': df['Count'].apply(parse_amount).astype(int),
})
seevplus = seevplus.groupby('month').agg({
    'seevplus_withdraw_ghs': 'sum',
    'seevplus_withdraw_fees_ghs': 'sum',
    'seevplus_withdraw_count': 'sum',
}).reset_index()

# 7. Transactions from SeevAPI Customers (GHS) — CORRECTED from USD
df = pd.read_csv(os.path.join(BASE_DIR, 'apitransactions.csv'))
df.columns = [c.strip() for c in df.columns]
api_txns = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_month),
    'api_txn_ghs': df['Sum of Amount'].apply(parse_amount),
    'api_txn_count': df['Count'].apply(parse_amount).astype(int),
})

# 8. Sum of Transaction P2P / Pay to Users (GHS) — CORRECTED from USD
df = pd.read_csv(os.path.join(BASE_DIR, 'sum_of_transaction_paytousers.csv'))
df.columns = [c.strip() for c in df.columns]
pay_to_users = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_month),
    'pay_to_users_ghs': df['Sum of TransactionAmount'].apply(parse_amount),
    'pay_to_users_count': df['Count'].apply(parse_amount).astype(int),
})

# 9. Cross-Border Transactions (GHS, weekly -> monthly) — CORRECTED from USD
df = pd.read_csv(os.path.join(BASE_DIR, 'cross_border_transactions.csv'))
df.columns = [c.strip() for c in df.columns]
cross_border = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_week_to_month),
    'cross_border_ghs': df['Sum of ToAmount'].apply(parse_amount),
})
cross_border = cross_border.groupby('month').agg({
    'cross_border_ghs': 'sum',
}).reset_index()

# ================================================================
# USD CHANNELS (2 channels — On-chain crypto only)
# ================================================================

# 10. On-chain Deposits (USD)
df = pd.read_csv(os.path.join(BASE_DIR, 'onchaintransactions__deposit.csv'))
df.columns = [c.strip() for c in df.columns]
onchain_deposit = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_month),
    'onchain_deposit_usd': df['Sum of TokenValue'].apply(parse_amount),
    'onchain_deposit_fees_usd': df['Sum of Fee'].apply(parse_amount),
})

# 11. On-chain Withdrawals (USD)
df = pd.read_csv(os.path.join(BASE_DIR, 'onchaintransactions__withdraw.csv'))
df.columns = [c.strip() for c in df.columns]
onchain_withdraw = pd.DataFrame({
    'month': df.iloc[:, 0].apply(parse_month),
    'onchain_withdraw_usd': df['Sum of TokenValue'].apply(parse_amount),
    'onchain_withdraw_fees_usd': df['Sum of Fee'].apply(parse_amount),
    'onchain_withdraw_count': df['Count'].apply(parse_amount).astype(int),
})


# ================================================================
# MERGE
# ================================================================
all_months = set()
for frame in [pay_to_momo, add_from_momo, withdraw_to_momo, mobile_request,
              api_txns, pay_to_users, pay_to_banks, onchain_deposit,
              onchain_withdraw, seevplus, cross_border]:
    all_months.update(frame['month'].dropna().tolist())

master = pd.DataFrame({'month': sorted(all_months)})

datasets = [pay_to_momo, add_from_momo, withdraw_to_momo, mobile_request,
            api_txns, pay_to_users, pay_to_banks, onchain_deposit,
            onchain_withdraw, seevplus, cross_border]

for ds in datasets:
    master = master.merge(ds, on='month', how='left')

master = master.fillna(0)
master = master.sort_values('month').reset_index(drop=True)

master['month_label'] = master['month'].dt.strftime('%b %Y')
master['year'] = master['month'].dt.year
master['month_num'] = master['month'].dt.month
master['ghs_usd_rate'] = master['month'].apply(get_rate)

# ================================================================
# Aggregated metrics — GHS and USD kept strictly separate
# ================================================================
ghs_vol_cols = [
    'pay_to_momo_ghs', 'add_from_momo_ghs', 'withdraw_to_momo_ghs',
    'mobile_request_ghs', 'pay_to_banks_ghs', 'seevplus_withdraw_ghs',
    'api_txn_ghs', 'pay_to_users_ghs', 'cross_border_ghs',
]
usd_vol_cols = [
    'onchain_deposit_usd', 'onchain_withdraw_usd',
]
ghs_fee_cols = [c for c in master.columns if 'fees_ghs' in c]
usd_fee_cols = [c for c in master.columns if 'fees_usd' in c]
count_cols = [c for c in master.columns if c.endswith('_count')]

master['total_volume_ghs'] = master[ghs_vol_cols].sum(axis=1)
master['total_volume_usd'] = master[usd_vol_cols].sum(axis=1)
master['total_fees_ghs'] = master[ghs_fee_cols].sum(axis=1)
master['total_fees_usd'] = master[usd_fee_cols].sum(axis=1)
master['total_transaction_count'] = master[count_cols].sum(axis=1)

meta_cols = ['month', 'month_label', 'year', 'month_num', 'ghs_usd_rate']
agg_cols = ['total_volume_ghs', 'total_volume_usd',
            'total_transaction_count', 'total_fees_ghs', 'total_fees_usd']
remaining = sorted([c for c in master.columns if c not in meta_cols + agg_cols])
master = master[meta_cols + agg_cols + remaining]

output_path = os.path.join(BASE_DIR, 'seevcash_compiled_data.csv')
master.to_csv(output_path, index=False)

print(f"Compiled dataset saved to: {output_path}")
print(f"Shape: {master.shape}")
print(f"Date range: {master['month'].min().strftime('%b %Y')} - {master['month'].max().strftime('%b %Y')}")
print(f"\nCurrency split (CORRECTED):")
print(f"  GHS (9 channels): Pay to MoMo, Add from MoMo, Withdraw to MoMo,")
print(f"                     Mobile Requests, Pay to Banks, SeevPlus Withdraw,")
print(f"                     SeevAPI (API Txns), P2P (Pay to Users), Cross-border")
print(f"  USD (2 channels):  On-chain Deposit, On-chain Withdraw")
print(f"\nMonthly summary (GHS and USD kept separate — no blending):")
print(master[['month_label', 'total_volume_ghs', 'total_volume_usd',
              'total_transaction_count', 'total_fees_ghs',
              'total_fees_usd']].to_string())
