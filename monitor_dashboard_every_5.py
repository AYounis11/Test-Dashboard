import streamlit as st
 
def check_password():
    def password_entered():
        if st.session_state["password_input"] == st.secrets.get("auth", {}).get("password"):
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False
 
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
 
    if not st.session_state["password_correct"]:
        st.text_input("Enter password:", type="password", key="password_input", on_change=password_entered)
        if st.session_state["password_correct"] == False and "password_input" in st.session_state:
            st.error("❌ Incorrect password")
        st.stop()
 
check_password()
  
st.write("Welcome! You have access to the dashboard.")

from pathlib import Path
import pandas as pd
from datetime import datetime
 
log_file = Path("web-monitor-structured-log.txt")
 
st.set_page_config(page_title="Website Monitoring Dashboard", layout="wide")
st.title("📶 Website Monitoring Dashboard")
st.markdown("Each monitored website has its own latency and TTL graph.")
st.markdown("🔄 Auto-refreshes every 30 seconds")
 
# Auto-refresh
st.markdown("""
<script>
        setTimeout(() => window.location.reload(), 30000);
</script>
""", unsafe_allow_html=True)
 
# Load and clean data
if not log_file.exists():
    st.error(f"❌ Log file not found at: {log_file}")
    st.stop()
 
try:
    df = pd.read_csv(
        log_file,
        encoding="utf-8",
        header=None,
        names=["Timestamp", "Website", "Status", "Latency(ms)", "TTL"],
        engine="python"
    )
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df = df.dropna(subset=["Timestamp"])
    df = df.sort_values("Timestamp", ascending=True)
except Exception as e:
    st.error(f"⚠️ Failed to load log file: {e}")
    st.stop()
 
# Website filter
sites = df["Website"].unique().tolist()
selected_sites = st.multiselect("Select websites to display:", sites, default=sites)
filtered_df = df[df["Website"].isin(selected_sites)]
 
# Color-coded latest status
st.subheader("📈 Latest Website Status")
latest_df = filtered_df.groupby("Website").last().reset_index()
def highlight_status(val):
    return "background-color: lightgreen" if val == "Success" else "background-color: salmon"
st.dataframe(latest_df.style.applymap(highlight_status, subset=["Status"]), use_container_width=True)
 
# Per-website line charts
for site in selected_sites:
    site_df = filtered_df[(filtered_df["Website"] == site)].copy()
    site_df["Latency(ms)"] = pd.to_numeric(site_df["Latency(ms)"], errors="coerce")
    site_df["TTL"] = pd.to_numeric(site_df["TTL"], errors="coerce")
 
    if site_df.empty:
        st.info(f"ℹ️ No successful data for {site} to plot.")
        continue
 
    st.subheader(f"📊 {site} - Latency Over Time")
    st.line_chart(site_df.set_index("Timestamp")["Latency(ms)"])
 
    st.subheader(f"🧭 {site} - TTL Over Time")
    st.line_chart(site_df.set_index("Timestamp")["TTL"])

# 🧠 AI Insights Section

st.subheader("🧠 AI Insights")

insight_messages = []

for site in selected_sites:
    site_df = filtered_df[filtered_df["Website"] == site].copy()
    site_df["Latency(ms)"] = pd.to_numeric(site_df["Latency(ms)"], errors="coerce")

    total_pings = len(site_df)
    if total_pings == 0:
        continue

    success_pings = len(site_df[site_df["Status"] == "Success"])
    zero_latency = len(site_df[(site_df["Latency(ms)"] == 0) & (site_df["Status"] == "Unreachable")])
    avg_latency = site_df[site_df["Status"] == "Success"]["Latency(ms)"].mean()
    high_latency = len(site_df[site_df["Latency(ms)"] > 200])  # Define 200ms as spike threshold

    uptime_percent = round((success_pings / total_pings) * 100, 2)

    insight = f"🔎 **{site}** — Uptime: **{uptime_percent}%**, Avg Latency: **{int(avg_latency)}ms**, "
    insight += f"High Latency Spikes: **{high_latency}**, Zero Latency Alerts: **{zero_latency}**"

    if high_latency > 0 or zero_latency > 0:
        st.warning(insight)
    else:
        st.success(insight)
