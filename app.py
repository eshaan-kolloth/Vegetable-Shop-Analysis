import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

# --- Page Config ---
st.set_page_config(
    page_title="Vegetable Shop Dashboard",
    page_icon="🥦",
    layout="wide"
)

# --- Load Data ---
@st.cache_data
def load_data():
    with open("data/vegetable_shop.csv", "r") as f:
        content = f.read()
    content = content.replace('"', '')
    df = pd.read_csv(StringIO(content))
    df["Date"] = pd.to_datetime(df["Date"])
    df["Revenue"] = df["Sold_kg"] * df["Sell_Price"]
    df["Cost"] = df["Bought_kg"] * df["Buy_Price"]
    df["Profit"] = df["Revenue"] - df["Cost"]
    return df

df = load_data()

# --- Sidebar ---
st.sidebar.title("🥦 Vegetable Shop")
st.sidebar.markdown("---")

# --- Page Navigation ---
st.sidebar.markdown("### 🗂️ Navigation")
page = st.sidebar.radio("Go to", ["📊 Dashboard", "📋 Summary", "📁 Raw Data"])

st.sidebar.markdown("---")

# --- Vegetable Filter ---
st.sidebar.markdown("### 🥕 Vegetables")
all_items = sorted(df["Item"].unique().tolist())
select_all_veg = st.sidebar.checkbox("Select All Vegetables", value=True)
if select_all_veg:
    selected_items = all_items
else:
    selected_items = st.sidebar.multiselect(
        "Choose vegetables",
        options=all_items,
        default=all_items
    )

st.sidebar.markdown("---")

# --- Day Filter ---
st.sidebar.markdown("### 📅 Day of Week")
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
available_days = [d for d in day_order if d in df["Day"].unique()]
select_all_days = st.sidebar.checkbox("Select All Days", value=True)
if select_all_days:
    selected_days = available_days
else:
    selected_days = []
    for day in available_days:
        if st.sidebar.checkbox(day, value=True):
            selected_days.append(day)

st.sidebar.markdown("---")

# --- Date Filter ---
st.sidebar.markdown("### 🗓️ Date Range")
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date)

st.sidebar.markdown("---")

# --- Filter Data ---
filtered_df = df[
    (df["Item"].isin(selected_items)) &
    (df["Day"].isin(selected_days)) &
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date))
].copy()

# ============================================================
# PAGE 1 — DASHBOARD
# ============================================================
if page == "📊 Dashboard":

    st.title("📊 Vegetable Shop Dashboard")
    st.caption(f"Showing data from {start_date} to {end_date} — {len(filtered_df)} records")
    st.markdown("---")

    # --- KPI Cards ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🛒 Total Bought", f"{filtered_df['Bought_kg'].sum():.1f} kg")
    with col2:
        st.metric("✅ Total Sold", f"{filtered_df['Sold_kg'].sum():.1f} kg")
    with col3:
        st.metric("🗑️ Total Wasted", f"{filtered_df['Wasted_kg'].sum():.1f} kg")
    with col4:
        st.metric("💰 Total Revenue", f"₹{filtered_df['Revenue'].sum():,.0f}")

    st.markdown("---")

    # --- Row 1: Bar Chart + Line Chart ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Sales by Vegetable")
        sales_by_item = filtered_df.groupby("Item")["Sold_kg"].sum().reset_index()
        fig1 = px.bar(
            sales_by_item, x="Item", y="Sold_kg", color="Item",
            title="Total Sold (kg) per Vegetable"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📈 Sales Over Time")
        sales_over_time = filtered_df.groupby("Date")["Sold_kg"].sum().reset_index()
        fig2 = px.line(
            sales_over_time, x="Date", y="Sold_kg",
            title="Daily Sales (kg) Over Time"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # --- Row 2: Waste Pie + Revenue Bar ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🗑️ Waste Analysis")
        waste_by_item = filtered_df.groupby("Item")["Wasted_kg"].sum().reset_index()
        fig3 = px.pie(
            waste_by_item, names="Item", values="Wasted_kg",
            title="Waste Distribution by Vegetable"
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.subheader("💰 Revenue by Vegetable")
        revenue_by_item = filtered_df.groupby("Item")["Revenue"].sum().reset_index()
        fig4 = px.bar(
            revenue_by_item, x="Item", y="Revenue", color="Item",
            title="Total Revenue (₹) per Vegetable"
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # --- Row 3: Profit Over Time + Bought vs Sold vs Wasted ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Profit Over Time")
        profit_over_time = filtered_df.groupby("Date")["Profit"].sum().reset_index()
        fig5 = px.area(
            profit_over_time, x="Date", y="Profit",
            title="Daily Profit (₹) Over Time",
            color_discrete_sequence=["#00cc96"]
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.subheader("⚖️ Bought vs Sold vs Wasted")
        compare_df = filtered_df.groupby("Item")[["Bought_kg", "Sold_kg", "Wasted_kg"]].sum().reset_index()
        fig6 = px.bar(
            compare_df, x="Item",
            y=["Bought_kg", "Sold_kg", "Wasted_kg"],
            title="Bought vs Sold vs Wasted per Vegetable",
            barmode="group"
        )
        st.plotly_chart(fig6, use_container_width=True)

    st.markdown("---")

    # --- Row 4: Weekend vs Weekday + Price Trend ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📅 Weekend vs Weekday Sales")
        filtered_df["Day_Type"] = filtered_df["Day"].apply(
            lambda x: "Weekend" if x in ["Saturday", "Sunday"] else "Weekday"
        )
        day_type_df = filtered_df.groupby("Day_Type")["Sold_kg"].sum().reset_index()
        fig7 = px.pie(
            day_type_df, names="Day_Type", values="Sold_kg",
            title="Weekend vs Weekday Sales",
            color_discrete_sequence=["#636EFA", "#EF553B"]
        )
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        st.subheader("💹 Average Sell Price Over Time")
        price_trend = filtered_df.groupby("Date")["Sell_Price"].mean().reset_index()
        fig8 = px.line(
            price_trend, x="Date", y="Sell_Price",
            title="Average Sell Price Over Time",
            color_discrete_sequence=["#FF7F0E"]
        )
        st.plotly_chart(fig8, use_container_width=True)

# ============================================================
# PAGE 2 — SUMMARY
# ============================================================
elif page == "📋 Summary":

    st.title("📋 Summary Page")
    st.caption(f"Showing data from {start_date} to {end_date}")
    st.markdown("---")

    # --- Compute Summary ---
    summary = filtered_df.groupby("Item").agg(
        Total_Sold=("Sold_kg", "sum"),
        Total_Wasted=("Wasted_kg", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Revenue=("Revenue", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Bought=("Bought_kg", "sum"),
        Avg_Sell_Price=("Sell_Price", "mean"),
        Avg_Buy_Price=("Buy_Price", "mean"),
    ).round(2).reset_index()

    best_seller = summary.loc[summary["Total_Sold"].idxmax(), "Item"]
    most_wasted = summary.loc[summary["Total_Wasted"].idxmax(), "Item"]
    most_profit = summary.loc[summary["Total_Profit"].idxmax(), "Item"]

    # --- Top 3 Highlight Cards ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(f"🏆 Best Seller\n\n# {best_seller}")
    with col2:
        st.error(f"🗑️ Most Wasted\n\n# {most_wasted}")
    with col3:
        st.info(f"💰 Most Profitable\n\n# {most_profit}")

    st.markdown("---")

    # --- Section 1: Best Seller ---
    st.subheader("🏆 Best Seller Analysis")
    col1, col2 = st.columns(2)

    with col1:
        fig_bs1 = px.bar(
            summary.sort_values("Total_Sold", ascending=False),
            x="Item", y="Total_Sold", color="Item",
            title="Total Sales (kg) — All Vegetables Ranked",
            labels={"Total_Sold": "Total Sold (kg)"}
        )
        st.plotly_chart(fig_bs1, use_container_width=True)

    with col2:
        fig_bs2 = px.bar(
            summary.sort_values("Total_Sold", ascending=True),
            x="Total_Sold", y="Item", color="Item",
            orientation="h",
            title="Sales Ranking (Horizontal View)",
            labels={"Total_Sold": "Total Sold (kg)"}
        )
        st.plotly_chart(fig_bs2, use_container_width=True)

    st.markdown("---")

    # --- Section 2: Most Wasted ---
    st.subheader("🗑️ Waste Analysis")
    col1, col2 = st.columns(2)

    with col1:
        fig_w1 = px.bar(
            summary.sort_values("Total_Wasted", ascending=False),
            x="Item", y="Total_Wasted", color="Item",
            title="Total Wasted (kg) — All Vegetables Ranked",
            labels={"Total_Wasted": "Total Wasted (kg)"},
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        st.plotly_chart(fig_w1, use_container_width=True)

    with col2:
        fig_w2 = px.pie(
            summary,
            names="Item", values="Total_Wasted",
            title="Waste Share by Vegetable",
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        st.plotly_chart(fig_w2, use_container_width=True)

    st.markdown("---")

    # --- Section 3: Most Profitable ---
    st.subheader("💰 Profitability Analysis")
    col1, col2 = st.columns(2)

    with col1:
        fig_p1 = px.bar(
            summary.sort_values("Total_Profit", ascending=False),
            x="Item", y="Total_Profit", color="Item",
            title="Total Profit (₹) — All Vegetables Ranked",
            labels={"Total_Profit": "Total Profit (₹)"},
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        st.plotly_chart(fig_p1, use_container_width=True)

    with col2:
        fig_p2 = px.bar(
            summary,
            x="Item",
            y=["Total_Revenue", "Total_Cost", "Total_Profit"],
            title="Revenue vs Cost vs Profit per Vegetable",
            barmode="group",
            labels={"value": "Amount (₹)", "variable": "Category"}
        )
        st.plotly_chart(fig_p2, use_container_width=True)

    st.markdown("---")

    # --- Section 4: Day of Week Analysis ---
    st.subheader("📅 Sales by Day of Week")
    day_sales = filtered_df.groupby("Day")["Sold_kg"].sum().reindex(day_order).reset_index()
    fig_day = px.bar(
        day_sales, x="Day", y="Sold_kg",
        title="Total Sales (kg) by Day of Week",
        color="Sold_kg",
        color_continuous_scale="Viridis",
        labels={"Sold_kg": "Total Sold (kg)"}
    )
    st.plotly_chart(fig_day, use_container_width=True)

    st.markdown("---")

    # --- Full Summary Table ---
    st.subheader("📊 Full Summary Table")
    st.dataframe(summary, use_container_width=True)

# ============================================================
# PAGE 3 — RAW DATA
# ============================================================
elif page == "📁 Raw Data":

    st.title("📁 Raw Data")
    st.caption(f"Showing {len(filtered_df)} records")
    st.markdown("---")

    # --- Search ---
    search = st.text_input("🔍 Search by vegetable name", "")
    if search:
        filtered_df = filtered_df[filtered_df["Item"].str.contains(search, case=False)]

    st.dataframe(filtered_df, use_container_width=True)

    st.markdown("---")

    # --- Download Button ---
    st.subheader("⬇️ Download Data")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="vegetable_shop_filtered.csv",
        mime="text/csv"
    )