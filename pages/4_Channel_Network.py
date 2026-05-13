import streamlit as st
import plotly.express as px

from utils.youtube import (
    load_channels,
    load_videos,
    load_growth,
    avg_views_per_video,
    views_by_duration_bin,
    views_by_category,
)

# ── Load YouTube data (static CSVs, not from session state) ───────────────────
if "youtube_channels" not in st.session_state:
    st.session_state["youtube_channels"] = load_channels()
    st.session_state["youtube_videos"] = load_videos()
    st.session_state["youtube_growth"] = load_growth()

channels_df = st.session_state["youtube_channels"]
videos_df = st.session_state["youtube_videos"]
growth_df = st.session_state["youtube_growth"]

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("Channel Network")
st.caption("Stakeholders: Commercial Team · Content Strategy · Ad Sales")
st.caption(
    "Data: Simulated from 20 LDS-managed channel archetypes. "
    "Network total: 800+ channels, 930M subscribers, 11.2B monthly views (LDS Whitepaper 2026)."
)

st.divider()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total_subs = int(channels_df["subscribers"].sum())
total_views = int(growth_df.groupby("channel_id")["monthly_views"].last().sum())
avg_vpv = avg_views_per_video(channels_df, videos_df)

k1, k2, k3 = st.columns(3)
k1.metric("Total Subscribers (Sample)", f"{total_subs / 1_000_000:.1f}M")
k2.metric("Est. Monthly Views (Sample)", f"{total_views / 1_000_000:.0f}M")
k3.metric("Avg Views per Video", f"{avg_vpv:,.0f}")

st.divider()

# ── Top Channels Leaderboard ──────────────────────────────────────────────────
st.subheader("Top Channels by Subscribers")

leaderboard = channels_df.sort_values("subscribers", ascending=False).copy()
leaderboard["Avg Views/Video"] = (leaderboard["total_views"] / leaderboard["video_count"]).round(0).astype(int)
leaderboard = leaderboard.rename(columns={
    "channel_name": "Channel",
    "category": "Category",
    "subscribers": "Subscribers",
    "total_views": "Total Views",
    "video_count": "Videos",
}).drop(columns=["channel_id"])

st.dataframe(
    leaderboard.style.format({
        "Subscribers": "{:,}",
        "Total Views": "{:,}",
        "Avg Views/Video": "{:,}",
    }),
    use_container_width=True,
)

st.divider()

# ── Subscriber Growth Trend (Top 5 Channels) ──────────────────────────────────
st.subheader("Subscriber Growth — Top 5 Channels")
st.caption("Monthly subscriber count for the 5 largest channels in the sample.")

top5_ids = channels_df.nlargest(5, "subscribers")["channel_id"].tolist()
top5_names = channels_df.set_index("channel_id")["channel_name"].to_dict()

growth_top5 = growth_df[growth_df["channel_id"].isin(top5_ids)].copy()
growth_top5["channel_name"] = growth_top5["channel_id"].map(top5_names)

fig_growth = px.line(
    growth_top5,
    x="month",
    y="subscriber_count",
    color="channel_name",
    color_discrete_sequence=["#E31837", "#1A1A1A", "#6D6E71", "#94A3B8", "#F59E0B"],
    labels={"month": "Month", "subscriber_count": "Subscribers", "channel_name": "Channel"},
    markers=True,
)
fig_growth.update_layout(
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font_color="#1A1A1A",
    yaxis_tickformat=",",
)
st.plotly_chart(fig_growth, use_container_width=True)

st.divider()

# ── Video Length vs Performance ────────────────────────────────────────────────
st.subheader("Video Length vs. Average Views")
st.caption(
    "LDS research: 45–60 min videos drive ~40% of network revenue. "
    "Does channel data support this? Longer content typically earns higher RPM."
)

bin_df = views_by_duration_bin(videos_df)
bin_df = bin_df.dropna(subset=["avg_views"])

fig_length = px.bar(
    bin_df,
    x="duration_bin",
    y="avg_views",
    color_discrete_sequence=["#E31837"],
    labels={"duration_bin": "Video Length", "avg_views": "Avg Views"},
)
fig_length.update_layout(
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font_color="#1A1A1A",
    xaxis_categoryorder="array",
    xaxis_categoryarray=["<10 min", "10-30 min", "30-45 min", "45-60 min", "60+ min"],
)
st.plotly_chart(fig_length, use_container_width=True)

st.divider()

# ── Content Category Breakdown ─────────────────────────────────────────────────
st.subheader("Views by Content Category")

cat_df = views_by_category(channels_df, videos_df)

fig_donut = px.pie(
    cat_df,
    names="category",
    values="total_views",
    hole=0.45,
    color_discrete_sequence=[
        "#E31837", "#1A1A1A", "#6D6E71", "#94A3B8", "#F59E0B", "#16A34A", "#3B82F6"
    ],
)
fig_donut.update_layout(
    paper_bgcolor="#FFFFFF",
    font_color="#1A1A1A",
)
st.plotly_chart(fig_donut, use_container_width=True)

st.divider()

# ── Underperforming Channels ───────────────────────────────────────────────────
st.subheader("Underperforming Channels")
st.caption("Channels with below-average views/video or declining subscriber trend (last 2 months).")

# Compute avg views per video per channel
channel_perf = videos_df.groupby("channel_id")["views"].mean().reset_index()
channel_perf.columns = ["channel_id", "avg_views_per_video"]
network_avg = channel_perf["avg_views_per_video"].mean()

# Check for subscriber decline: last month vs. month before
latest_two = growth_df.sort_values("month").groupby("channel_id").tail(2)
sub_change = (
    latest_two.groupby("channel_id")["subscriber_count"]
    .apply(lambda s: s.iloc[-1] - s.iloc[0] if len(s) == 2 else 0)
    .reset_index()
    .rename(columns={"subscriber_count": "sub_change_mom"})
)

underperf = channel_perf.merge(sub_change, on="channel_id").merge(
    channels_df[["channel_id", "channel_name", "video_count"]], on="channel_id"
)

flags = underperf[
    (underperf["avg_views_per_video"] < network_avg * 0.6)
    | (underperf["sub_change_mom"] < 0)
]

if len(flags) == 0:
    st.success("No underperforming channels detected in this sample.")
else:
    for _, row in flags.iterrows():
        issues = []
        if row["avg_views_per_video"] < network_avg * 0.6:
            issues.append(f"avg views/video {row['avg_views_per_video']:,.0f} (network avg: {network_avg:,.0f})")
        if row["sub_change_mom"] < 0:
            issues.append(f"subscribers down {abs(int(row['sub_change_mom'])):,} MoM")
        st.warning(
            f"**{row['channel_name']}** — {' · '.join(issues)}"
        )
