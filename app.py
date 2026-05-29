import os

import streamlit as st
import duckdb
import plotly.express as px

from pipeline import run_nba_etl

DB_PATH = "nba_warehouse.db"

st.set_page_config(page_title="NBA Analytics Warehouse", page_icon="🏀", layout="wide")
st.title("🏀 NBA Team Analytics Warehouse Dashboard")

# --- Sidebar ---
with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Trigger Data Pipeline ETL"):
        with st.spinner("Running ETL pipeline..."):
            run_nba_etl()
        st.success("ETL pipeline completed successfully!")

    st.divider()
    st.header("Filters")

if not os.path.exists(DB_PATH):
    st.info("No data yet. Click '🔄 Trigger Data Pipeline ETL' in the sidebar to populate the dashboard.")
    st.stop()

con = duckdb.connect(DB_PATH, read_only=True)
df = con.execute("SELECT * FROM analytics_team_standings").df()
try:
    df_leaders = con.execute("SELECT * FROM analytics_league_leaders").df()
except Exception:
    df_leaders = None
con.close()

# --- Sidebar filters ---
with st.sidebar:
    teams = sorted(df["TEAM_NAME"].unique())
    selected_teams = st.multiselect("Select Teams", teams, default=teams)
    gp_min, gp_max = int(df["GP"].min()), int(df["GP"].max())
    if gp_min < gp_max:
        min_gp = st.slider("Minimum Games Played", gp_min, gp_max, gp_min)
    else:
        min_gp = gp_min

filtered_df = df[(df["TEAM_NAME"].isin(selected_teams)) & (df["GP"] >= min_gp)]

if filtered_df.empty:
    st.warning("No teams match the current filters.")
    st.stop()

# --- KPI Metrics ---
st.subheader("📊 League Snapshot")
col1, col2, col3, col4 = st.columns(4)
best_team = filtered_df.iloc[0]
col1.metric("Best Record", best_team["TEAM_NAME"], f"{best_team['W']}W - {best_team['L']}L")
col2.metric("Highest Win %", f"{filtered_df['W_PCT'].max():.3f}")
col3.metric("Avg Offensive Efficiency", f"{filtered_df['OFFENSIVE_EFFICIENCY'].mean():.1f}")
col4.metric("Teams Shown", len(filtered_df))

st.divider()

# --- Data Table ---
st.subheader("📋 Team Standings")
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# --- Scatter Plot ---
st.subheader("🔬 Win % vs Offensive Efficiency")
fig_scatter = px.scatter(
    filtered_df,
    x="W_PCT",
    y="OFFENSIVE_EFFICIENCY",
    hover_name="TEAM_NAME",
    size="GP",
    color="W_PCT",
    color_continuous_scale="Viridis",
    labels={
        "W_PCT": "Win Percentage",
        "OFFENSIVE_EFFICIENCY": "Offensive Efficiency ((PTS + AST) / GP)",
        "GP": "Games Played",
    },
    title="Win Percentage vs Offensive Efficiency",
)
fig_scatter.update_layout(height=500)
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# --- Team Comparison Tool ---
st.subheader("⚔️ Head-to-Head Team Comparison")
comp_col1, comp_col2 = st.columns(2)
available = filtered_df["TEAM_NAME"].tolist()

with comp_col1:
    team_a = st.selectbox("Team A", available, index=0)
with comp_col2:
    team_b = st.selectbox("Team B", available, index=min(1, len(available) - 1))

if team_a and team_b:
    compare_df = filtered_df[filtered_df["TEAM_NAME"].isin([team_a, team_b])].set_index("TEAM_NAME")
    metrics = ["GP", "W", "L", "W_PCT", "PTS", "AST", "OFFENSIVE_EFFICIENCY"]
    compare_display = compare_df[metrics].T
    compare_display.columns.name = None

    st.dataframe(compare_display, use_container_width=True)

    fig_compare = px.bar(
        compare_df[metrics].reset_index().melt(id_vars="TEAM_NAME", var_name="Metric", value_name="Value"),
        x="Metric",
        y="Value",
        color="TEAM_NAME",
        barmode="group",
        title=f"{team_a} vs {team_b}",
        height=400,
    )
    st.plotly_chart(fig_compare, use_container_width=True)

st.divider()

# --- League Leaders ---
st.subheader("🏆 League Leaders")
if df_leaders is not None and not df_leaders.empty:
    cat_col1, cat_col2, cat_col3, cat_col4, cat_col5 = st.columns(5)

    top_n = st.slider("Show top N players", 5, 25, 10, key="leaders_top_n")

    with cat_col1:
        st.markdown("**Points**")
        pts_leaders = df_leaders.nlargest(top_n, "PTS")[["PLAYER", "TEAM", "PTS"]]
        st.dataframe(pts_leaders, hide_index=True, use_container_width=True)

    with cat_col2:
        st.markdown("**Assists**")
        ast_leaders = df_leaders.nlargest(top_n, "AST")[["PLAYER", "TEAM", "AST"]]
        st.dataframe(ast_leaders, hide_index=True, use_container_width=True)

    with cat_col3:
        st.markdown("**Rebounds**")
        reb_leaders = df_leaders.nlargest(top_n, "REB")[["PLAYER", "TEAM", "REB"]]
        st.dataframe(reb_leaders, hide_index=True, use_container_width=True)

    with cat_col4:
        st.markdown("**Steals**")
        stl_leaders = df_leaders.nlargest(top_n, "STL")[["PLAYER", "TEAM", "STL"]]
        st.dataframe(stl_leaders, hide_index=True, use_container_width=True)

    with cat_col5:
        st.markdown("**Blocks**")
        blk_leaders = df_leaders.nlargest(top_n, "BLK")[["PLAYER", "TEAM", "BLK"]]
        st.dataframe(blk_leaders, hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("📈 Top Scorers")
    fig_leaders = px.bar(
        df_leaders.nlargest(15, "PTS"),
        x="PLAYER",
        y="PTS",
        color="TEAM",
        title="Top 15 Scorers",
        labels={"PTS": "Total Points", "PLAYER": ""},
        height=450,
    )
    fig_leaders.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_leaders, use_container_width=True)
else:
    st.info("League leaders data not available. Re-run the ETL pipeline to fetch player stats.")
