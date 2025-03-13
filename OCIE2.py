import streamlit as st
import pandas as pd
import plotly.express as px

# Load CSV files
@st.cache_data
def load_data():
    discharge_df = pd.read_csv("consolidated_discharge.csv")
    bde_df = pd.read_csv("BDE.csv")
    return discharge_df, bde_df

# Load datasets
discharge_df, bde_df = load_data()

# Convert date column
discharge_df["DISCHARGE_DT"] = pd.to_datetime(discharge_df["DISCHARGE_DT"])

# Merge Datasets on LOSS_UIC and UIC to bring in nm.BDE from bde_df
merged_df = discharge_df.merge(
    bde_df, left_on="LOSS_UIC", right_on="UIC", how="left"
)

# Sidebar filters
st.sidebar.header("Filters")

# Date filter
min_date = merged_df["DISCHARGE_DT"].min()
max_date = merged_df["DISCHARGE_DT"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# BDE Selection
bde_list = merged_df["nm.BDE"].dropna().unique()
selected_bde = st.sidebar.selectbox("Select BDE", ["All"] + list(bde_list))

# Filter data based on selections
filtered_data = merged_df[
    (merged_df["DISCHARGE_DT"] >= pd.to_datetime(date_range[0])) & 
    (merged_df["DISCHARGE_DT"] <= pd.to_datetime(date_range[1]))
]

# If a specific BDE is selected, filter data further
if selected_bde != "All":
    filtered_data = filtered_data[filtered_data["nm.BDE"] == selected_bde]

# --- 📌 Summary Insights Box ---
st.subheader("📌 Key Insights")

# Group by BDE & sum loss
bde_loss = (
    filtered_data.groupby(["nm.BDE"])
    .agg({"LOSS": "sum"})
    .reset_index()
)

# Find top BDE with highest loss
top_bde = bde_loss.loc[bde_loss["LOSS"].idxmax()]["nm.BDE"]
top_loss = bde_loss["LOSS"].max()

# Calculate total & average loss
total_loss = bde_loss["LOSS"].sum()
avg_loss = bde_loss["LOSS"].mean()

# Display insights
st.markdown(f"""
🔹 **Top BDE with Highest Loss:** {top_bde} (${top_loss:,.2f})  
🔹 **Total OCIE Loss:** ${total_loss:,.2f}  
🔹 **Average Loss per BDE:** ${avg_loss:,.2f}  
""")

# --- 📊 OCIE Loss Trend ---
st.subheader("📊 OCIE Loss Trend (Last 2 Years)")

loss_trend = (
    filtered_data.groupby(filtered_data["DISCHARGE_DT"].dt.to_period("M"))
    .agg({"LOSS": "sum"})
    .reset_index()
)
loss_trend["DISCHARGE_DT"] = loss_trend["DISCHARGE_DT"].astype(str)

fig = px.line(
    loss_trend, x="DISCHARGE_DT", y="LOSS", 
    title="Monthly OCIE Loss Trend", markers=True
)
st.plotly_chart(fig)

# --- 🚦 Stoplight Framework for BDE/DRU ---
st.subheader("🚦 OCIE Loss by BDE/DRU (Stoplight Framework)")

# Calculate % Change from Previous Period
bde_loss["Previous LOSS"] = bde_loss["LOSS"].shift(1)
bde_loss["% Change"] = ((bde_loss["LOSS"] - bde_loss["Previous LOSS"]) / bde_loss["Previous LOSS"]) * 100

# Fix TypeError by ensuring numeric conversion
bde_loss["% Change"] = bde_loss["% Change"].fillna(0).astype(float)

# Function to add trend arrows 📈📉
def add_trend_arrow(value):
    try:
        value = float(value)  # Ensure it's numeric
        if value > 0:
            return f"🔺 {value:+.2f}%"
        elif value < 0:
            return f"🔻 {value:+.2f}%"
        else:
            return f"➖ {value:+.2f}%"
    except ValueError:
        return "➖ 0.00%"  # Default for unexpected values

# Apply trend arrows to % Change column
bde_loss["% Change"] = bde_loss["% Change"].apply(add_trend_arrow)

st.dataframe(bde_loss)

# --- 🥧 Pie Chart for OCIE Loss by BDE ---
st.subheader("🥧 OCIE Loss Distribution by BDE")

fig_pie = px.pie(
    bde_loss, 
    names="nm.BDE", 
    values="LOSS",
    title="Proportion of OCIE Loss by BDE",
    hole=0.4  
)
st.plotly_chart(fig_pie)

# --- 📋 UIC Breakdown (Worst Offenders) ---
st.subheader("📋 UIC Breakdown with Loss % Change")

uic_loss = (
    filtered_data.groupby(["nm.BDE", "UIC"])
    .agg({"LOSS": "sum"})
    .reset_index()
)

# Calculate % Change from Previous Period
uic_loss["Previous LOSS"] = uic_loss.groupby(["nm.BDE", "UIC"])["LOSS"].shift(1)
uic_loss["% Change"] = ((uic_loss["LOSS"] - uic_loss["Previous LOSS"]) / uic_loss["Previous LOSS"]) * 100

# Fix TypeError by ensuring numeric conversion
uic_loss["% Change"] = uic_loss["% Change"].fillna(0).astype(float)

# Apply trend arrows to % Change column
uic_loss["% Change"] = uic_loss["% Change"].apply(add_trend_arrow)

st.dataframe(uic_loss)
