import random
import time
import streamlit as st
import pandas as pd

INITIAL_BALANCE = 100.00
INITIAL_STAKE = 1.00
DEFAULT_MULTIPLIER = 2.0
DEFAULT_TRADE_LIMIT = 10

st.set_page_config(page_title="Trader Tamim - Demo Bot", page_icon="📊", layout="wide")
st.title("📊 Trader Tamim — Trading Bot Demo")
st.caption("Virtual simulation only • No real money • No broker/API connection")

defaults = {
    "balance": INITIAL_BALANCE,
    "stake": INITIAL_STAKE,
    "prediction": 5,
    "contract_type": "DIGITOVER",
    "trades": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def simulate_trade():
    stake = float(st.session_state.stake)
    prediction = int(st.session_state.prediction)
    contract_type = st.session_state.contract_type
    digit = random.randint(0, 9)

    win = digit > prediction if contract_type == "DIGITOVER" else digit < prediction

    if win:
        profit = round(stake * 0.90, 2)
        result = "WIN"
        st.session_state.balance += profit
        st.session_state.stake = INITIAL_STAKE
        st.session_state.prediction = 5
        st.session_state.contract_type = "DIGITOVER"
    else:
        profit = -stake
        result = "LOSS"
        st.session_state.balance += profit
        st.session_state.stake = round(stake * st.session_state.multiplier, 2)
        st.session_state.contract_type = "DIGITUNDER"
        st.session_state.prediction = prediction - 1 if prediction > 1 else 3

    st.session_state.trades.append({
        "Trade": len(st.session_state.trades) + 1,
        "Type": contract_type,
        "Prediction": prediction,
        "Digit": digit,
        "Stake": round(stake, 2),
        "Result": result,
        "P/L": round(profit, 2),
        "Balance": round(st.session_state.balance, 2),
    })

st.sidebar.header("⚙️ Bot Settings")
initial_stake = st.sidebar.number_input("Initial Stake ($)", 0.10, 100.00, INITIAL_STAKE, 0.10)
st.session_state.multiplier = st.sidebar.number_input(
    "Martingale Multiplier", 1.0, 10.0, DEFAULT_MULTIPLIER, 0.5
)
trade_limit = st.sidebar.number_input("Trade Limit", 1, 100, DEFAULT_TRADE_LIMIT, 1)

if not st.session_state.trades:
    st.session_state.stake = initial_stake

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("▶️ Run Next Trade", use_container_width=True):
        if len(st.session_state.trades) < trade_limit:
            simulate_trade()
            st.rerun()
        else:
            st.warning("Trade limit reached.")
with c2:
    if st.button("🚀 Run All Trades", use_container_width=True):
        remaining = trade_limit - len(st.session_state.trades)
        if remaining > 0:
            progress = st.progress(0)
            for i in range(remaining):
                simulate_trade()
                progress.progress((i + 1) / remaining)
                time.sleep(0.15)
            st.rerun()
        else:
            st.warning("Trade limit reached.")
with c3:
    if st.button("🔄 Reset Demo", use_container_width=True):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()

trades = st.session_state.trades
wins = sum(x["Result"] == "WIN" for x in trades)
losses = sum(x["Result"] == "LOSS" for x in trades)
pnl = round(st.session_state.balance - INITIAL_BALANCE, 2)
win_rate = round(wins / len(trades) * 100, 2) if trades else 0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("💰 Balance", f"${st.session_state.balance:.2f}")
m2.metric("📈 Total P/L", f"${pnl:.2f}")
m3.metric("🎯 Win Rate", f"{win_rate}%")
m4.metric("✅ Wins", wins)
m5.metric("❌ Losses", losses)

st.subheader("🤖 Current Bot State")
s1, s2, s3 = st.columns(3)
s1.info(f"Next Stake: **${st.session_state.stake:.2f}**")
s2.info(f"Prediction: **{st.session_state.prediction}**")
s3.info(f"Contract: **{st.session_state.contract_type}**")

st.subheader("📋 Trade History")
if trades:
    df = pd.DataFrame(trades)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.subheader("📈 Virtual Balance")
    st.line_chart(df[["Trade", "Balance"]].set_index("Trade"))
else:
    st.info("No demo trades yet. Click 'Run Next Trade' to start.")

st.divider()
st.caption(
    "⚠️ Educational simulation only. Digits and outcomes are randomly generated; "
    "this does not predict real-market results."
)
