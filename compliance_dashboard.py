import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sqlalchemy import create_engine

# Database Setup
DB_FILE = "compliance_dashboard.db"
engine = create_engine(f"sqlite:///{DB_FILE}")
engine = create_engine("sqlite:///:memory:")  # In-memory SQLite for Streamlit Cloud
conn = engine.connect()
# Function to Generate Dummy Compliance Data
def generate_dummy_data():
    data = {
        "Trade_ID": [f"T{i}" for i in range(1, 501)],
        "Trader_ID": np.random.randint(1000, 2000, 500),
        "Exchange": np.random.choice(["Binance", "Coinbase", "Kraken", "FTX"], 500),
        "Asset": np.random.choice(["BTC/USD", "ETH/USD", "XRP/USD", "SOL/USD"], 500),
        "Risk_Score": np.random.uniform(0, 100, 500),
        "KYC_Status": np.random.choice(["Verified", "Unverified", "Blacklisted"], 500),
        "Transaction_Flag": np.random.choice(["Normal", "Suspicious"], 500, p=[0.85, 0.15]),
        "Trade_Amount": np.random.uniform(500, 100000, 500)
    }
    df = pd.DataFrame(data)
    df.to_sql("compliance_data", engine, if_exists="replace", index=False)
    return df

# Load Data from Database
def load_data():
    return pd.read_sql("SELECT * FROM compliance_data", conn)

# Streamlit App Configuration
st.set_page_config(page_title="Compliance Risk Dashboard", layout="wide")
st.title("📊 Compliance Risk Monitoring Dashboard")

# Load Data
df = load_data()

# Sidebar Filters
st.sidebar.header("Filter Data")
exchange_filter = st.sidebar.multiselect("Select Exchange", df["Exchange"].unique(), default=df["Exchange"].unique())
kyc_filter = st.sidebar.multiselect("Select KYC Status", df["KYC_Status"].unique(), default=df["KYC_Status"].unique())
transaction_filter = st.sidebar.multiselect("Select Transaction Type", df["Transaction_Flag"].unique(), default=df["Transaction_Flag"].unique())

# Apply Filters
df_filtered = df[(df["Exchange"].isin(exchange_filter)) &
                 (df["KYC_Status"].isin(kyc_filter)) &
                 (df["Transaction_Flag"].isin(transaction_filter))]

# Display Key Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", len(df_filtered))
col2.metric("High-Risk Transactions", len(df_filtered[df_filtered["Risk_Score"] > 80]))
col3.metric("Blacklisted Traders", len(df_filtered[df_filtered["KYC_Status"] == "Blacklisted"]))

# Risk Score Distribution
st.subheader("Risk Score Distribution")
fig_risk = px.histogram(df_filtered, x="Risk_Score", nbins=30, color_discrete_sequence=["red"])
st.plotly_chart(fig_risk, use_container_width=True)

# Transaction Amount by Exchange
st.subheader("Transaction Amount by Exchange")
fig_amount = px.bar(df_filtered, x="Exchange", y="Trade_Amount", color="Exchange", barmode="group")
st.plotly_chart(fig_amount, use_container_width=True)

# Suspicious Transactions Table
st.subheader("🚨 Suspicious Transactions")
st.dataframe(df_filtered[df_filtered["Transaction_Flag"] == "Suspicious"][
    ["Trade_ID", "Trader_ID", "Exchange", "Asset", "Risk_Score", "KYC_Status", "Trade_Amount"]])
