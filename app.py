"""
ARR Performance & Retention Intelligence
A lightweight local BI dashboard (Streamlit) demonstrating:
Raw data -> Data preparation -> KPI definition -> BI dashboard -> Business insights -> AI-style narrative layer

Data: fully local, anonymized CSV files (no database, no cloud, no API keys required for V1).
Run:  streamlit run app.py
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="ARR Performance & Retention Intelligence", layout="wide")

# ---------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------
@st.cache_data
def load_data():
    team_df = pd.read_csv("team_arr_2024.csv")
    yearly_df = pd.read_csv("yearly_overview.csv")
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4}
    team_df["MonthNum"] = team_df["Month"].map(month_order)
    team_df = team_df.sort_values("MonthNum")
    return team_df, yearly_df

team_df, yearly_df = load_data()

# ---------------------------------------------------------------
# SIDEBAR — FILTERS & NAVIGATION
# ---------------------------------------------------------------
st.sidebar.title("ARR Intelligence")
st.sidebar.caption("Data anonymized for demonstration. Local prototype — no database, no cloud.")

page = st.sidebar.radio(
    "Navigate",
    ["Executive Overview", "Team Performance", "Retention & Churn"],
)

all_months = list(team_df["Month"].unique())
selected_months = st.sidebar.multiselect("Month", all_months, default=all_months)

all_teams = sorted(team_df["Team"].unique())
selected_teams = st.sidebar.multiselect("Region", all_teams, default=all_teams)

filtered = team_df[
    team_df["Month"].isin(selected_months) & team_df["Team"].isin(selected_teams)
]

# ---------------------------------------------------------------
# HELPER — SIMPLE RULE-BASED "AI" INSIGHT ENGINE (V1, no external API)
# ---------------------------------------------------------------
def generate_insight(df: pd.DataFrame) -> str:
    if df.empty:
        return "No data available for the selected filters."

    total_lost = df["Lost_ARR"].sum()
    total_lost_count = df["Lost_Count"].sum()
    by_team = df.groupby("Team").agg(
        Lost_ARR=("Lost_ARR", "sum"),
        Lost_Count=("Lost_Count", "sum"),
        Expansion_ARR=("Expansion_ARR", "sum"),
        Net=("Net_ARR_Movement", "sum"),
    ).reset_index()

    if by_team.empty or total_lost == 0:
        return "No churn activity detected in the selected period."

    top_risk = by_team.sort_values("Lost_ARR", ascending=False).iloc[0]
    arr_share = top_risk["Lost_ARR"] / total_lost * 100
    cust_share = top_risk["Lost_Count"] / total_lost_count * 100 if total_lost_count else 0
    best_growth = by_team.sort_values("Net", ascending=False).iloc[0]

    concentration_note = (
        "concentrated among a relatively small number of higher-value accounts"
        if arr_share > cust_share + 10
        else "spread broadly across many accounts rather than a few large ones"
    )

    insight = (
        f"**{top_risk['Team']}** is the primary driver of ARR risk in this period, "
        f"contributing **{arr_share:.0f}%** of total Lost ARR while representing "
        f"**{cust_share:.0f}%** of lost customers. This suggests the loss is {concentration_note}. "
        f"Meanwhile, **{best_growth['Team']}** shows the strongest Net ARR Movement "
        f"(€{best_growth['Net']:,.0f}), making it the most resilient region in the selected period."
    )
    return insight

# ---------------------------------------------------------------
# PAGE 1 — EXECUTIVE OVERVIEW
# ---------------------------------------------------------------
if page == "Executive Overview":
    st.title("Executive Overview")
    st.caption("How is ARR performing across the business?")

    total_expansion = filtered["Expansion_ARR"].sum()
    total_contraction = filtered["Contraction_ARR"].sum()
    total_lost = filtered["Lost_ARR"].sum()
    net_movement = total_expansion + total_contraction - total_lost

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Expansion ARR", f"€{total_expansion:,.0f}")
    c2.metric("Contraction ARR", f"€{total_contraction:,.0f}")
    c3.metric("Lost ARR", f"€{total_lost:,.0f}")
    c4.metric("Net ARR Movement", f"€{net_movement:,.0f}")

    st.divider()

    monthly = filtered.groupby("Month", as_index=False).agg(
        Expansion_ARR=("Expansion_ARR", "sum"),
        Contraction_ARR=("Contraction_ARR", "sum"),
        Lost_ARR=("Lost_ARR", "sum"),
        Net_ARR_Movement=("Net_ARR_Movement", "sum"),
    )
    month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4}
    monthly["MonthNum"] = monthly["Month"].map(month_order)
    monthly = monthly.sort_values("MonthNum")

    fig = go.Figure()
    fig.add_bar(x=monthly["Month"], y=monthly["Expansion_ARR"], name="Expansion ARR", marker_color="#2ca02c")
    fig.add_bar(x=monthly["Month"], y=monthly["Contraction_ARR"], name="Contraction ARR", marker_color="#ff7f0e")
    fig.add_bar(x=monthly["Month"], y=-monthly["Lost_ARR"], name="Lost ARR", marker_color="#d62728")
    fig.add_scatter(x=monthly["Month"], y=monthly["Net_ARR_Movement"], name="Net ARR Movement",
                     mode="lines+markers", line=dict(color="#1f77b4", width=3))
    fig.update_layout(barmode="relative", title="Monthly ARR Movement (2024)", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Renewed vs Churned ARR — 2024 vs 2023 vs 2022")
    yearly_pivot = yearly_df.pivot_table(index="Month", columns="Year", values=["Renewed_ARR", "Churned_ARR"])
    fig2 = px.line(
        yearly_df.dropna(subset=["Renewed_ARR"]),
        x="Month", y="Renewed_ARR", color="Year", markers=True,
        title="Renewed ARR by Month — Year over Year",
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Note: 2024 data available for Jan–Apr only. May–Dec are not shown (no fabricated figures).")

    st.divider()
    st.subheader("AI Business Insight")
    st.info(generate_insight(filtered))

# ---------------------------------------------------------------
# PAGE 2 — TEAM PERFORMANCE
# ---------------------------------------------------------------
elif page == "Team Performance":
    st.title("Team Performance")
    st.caption("Which regions are driving growth, and which are creating ARR risk?")

    team_summary = filtered.groupby("Team", as_index=False).agg(
        Expansion_ARR=("Expansion_ARR", "sum"),
        Contraction_ARR=("Contraction_ARR", "sum"),
        Lost_ARR=("Lost_ARR", "sum"),
        Net_ARR_Movement=("Net_ARR_Movement", "sum"),
    ).sort_values("Net_ARR_Movement", ascending=False)

    st.dataframe(
        team_summary.style.format({
            "Expansion_ARR": "€{:,.0f}", "Contraction_ARR": "€{:,.0f}",
            "Lost_ARR": "€{:,.0f}", "Net_ARR_Movement": "€{:,.0f}",
        }),
        use_container_width=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        fig3 = px.bar(team_summary, x="Team", y="Net_ARR_Movement", color="Net_ARR_Movement",
                       color_continuous_scale="RdYlGn", title="Net ARR Movement by Region")
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        fig4 = px.bar(team_summary, x="Team", y="Lost_ARR", title="Lost ARR by Region",
                       color="Lost_ARR", color_continuous_scale="Reds")
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    st.subheader("Expansion vs Contraction vs Lost — by Region and Month")
    fig5 = px.bar(
        filtered, x="Month", y="Net_ARR_Movement", color="Team", barmode="group",
        title="Net ARR Movement Trend by Region",
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.divider()
    st.subheader("AI Business Insight")
    st.info(generate_insight(filtered))

# ---------------------------------------------------------------
# PAGE 3 — RETENTION & CHURN
# ---------------------------------------------------------------
else:
    st.title("ARR Retention & Risk")
    st.caption("Where are we losing ARR, and how significant is the risk?")

    total_lost = filtered["Lost_ARR"].sum()
    total_lost_count = filtered["Lost_Count"].sum()
    total_contraction = filtered["Contraction_ARR"].sum()
    total_contraction_count = filtered["Contraction_Count"].sum()
    avg_lost_per_customer = total_lost / total_lost_count if total_lost_count else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lost ARR", f"€{total_lost:,.0f}")
    c2.metric("Lost Customers", f"{total_lost_count:,.0f}")
    c3.metric("Contraction ARR", f"€{total_contraction:,.0f}")
    c4.metric("Avg ARR Lost / Customer", f"€{avg_lost_per_customer:,.0f}")

    st.divider()

    risk_df = filtered.groupby("Team", as_index=False).agg(
        Lost_ARR=("Lost_ARR", "sum"),
        Lost_Count=("Lost_Count", "sum"),
    )
    risk_df["ARR_share_%"] = (risk_df["Lost_ARR"] / risk_df["Lost_ARR"].sum() * 100).round(1)
    risk_df["Customer_share_%"] = (risk_df["Lost_Count"] / risk_df["Lost_Count"].sum() * 100).round(1)
    risk_df["Concentration_Gap"] = (risk_df["ARR_share_%"] - risk_df["Customer_share_%"]).round(1)

    fig6 = px.scatter(
        risk_df, x="Lost_Count", y="Lost_ARR", size="Lost_ARR", color="Team", text="Team",
        title="ARR Loss vs Customer Count by Region",
    )
    fig6.update_traces(textposition="top center")
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Churn Concentration Analysis")
    st.caption("A positive Concentration Gap means ARR loss is concentrated in fewer, higher-value accounts.")
    st.dataframe(
        risk_df.style.format({
            "Lost_ARR": "€{:,.0f}", "ARR_share_%": "{:.1f}%",
            "Customer_share_%": "{:.1f}%", "Concentration_Gap": "{:+.1f} pts",
        }),
        use_container_width=True,
    )

    st.divider()
    fig7 = px.line(
        filtered.groupby("Month", as_index=False)["Lost_ARR"].sum(),
        x="Month", y="Lost_ARR", markers=True, title="Lost ARR Trend (2024)",
    )
    st.plotly_chart(fig7, use_container_width=True)

    st.divider()
    st.subheader("AI Business Insight")
    st.info(generate_insight(filtered))
