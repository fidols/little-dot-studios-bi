"""
Seeded generator for simulated YouTube channel, video, and growth data.
Calibrated to LDS whitepaper figures: 930M subscribers, 11.2B monthly views.
Run once: python data/youtube/simulate_youtube.py
Outputs: channels.csv, videos.csv, growth.csv in the same directory.
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

SEED = 42
RNG = np.random.default_rng(SEED)
OUT_DIR = Path(__file__).parent

# 20 simulated LDS-managed channels
CHANNELS = [
    ("CH001", "Formula Classics",      "Sports",           8_500_000,  180, 2_100_000_000),
    ("CH002", "McLaren Moments",        "Sports",           4_200_000,   95,   820_000_000),
    ("CH003", "Olympic Highlights",     "Sports",          12_000_000,  220, 2_800_000_000),
    ("CH004", "Premier Motorsport",     "Sports",           3_100_000,  110,   650_000_000),
    ("CH005", "Speed & Style",          "Auto & Transport", 2_400_000,   88,   430_000_000),
    ("CH006", "Auto Reviews UK",        "Auto & Transport", 1_800_000,   76,   310_000_000),
    ("CH007", "History Vault",          "Documentary",      6_200_000,  410, 1_400_000_000),
    ("CH008", "Science Unlocked",       "Documentary",      3_800_000,  290,   760_000_000),
    ("CH009", "World Documentaries",    "Documentary",      2_100_000,  160,   490_000_000),
    ("CH010", "Daily Entertainment",    "Entertainment",   18_500_000,  520, 4_200_000_000),
    ("CH011", "Pop Culture Weekly",     "Entertainment",    9_300_000,  380, 2_100_000_000),
    ("CH012", "Classic Cinema",         "Entertainment",    4_600_000,  240,   980_000_000),
    ("CH013", "Comedy Central UK",      "Entertainment",    7_200_000,  310, 1_600_000_000),
    ("CH014", "Travel & Lifestyle",     "Lifestyle",        3_400_000,  195,   640_000_000),
    ("CH015", "Food & Travel",          "Lifestyle",        2_900_000,  175,   510_000_000),
    ("CH016", "Outdoor Adventures",     "Lifestyle",        1_500_000,   90,   270_000_000),
    ("CH017", "Business Insider UK",    "News",             5_100_000,  480, 1_200_000_000),
    ("CH018", "Sports Highlights",      "Sports",           6_800_000,  260, 1_500_000_000),
    ("CH019", "Gaming World",           "Sports & Gaming",  4_100_000,  820,   940_000_000),
    ("CH020", "Tech Today",             "Technology",       2_800_000,  210,   590_000_000),
]

TODAY = date(2026, 5, 12)


def generate_channels() -> pd.DataFrame:
    rows = []
    for ch_id, name, category, subs, video_count, total_views in CHANNELS:
        rows.append({
            "channel_id": ch_id,
            "channel_name": name,
            "subscribers": subs,
            "total_views": total_views,
            "video_count": video_count,
            "category": category,
        })
    return pd.DataFrame(rows)


def generate_videos(channels_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    vid_id = 1
    for _, ch in channels_df.iterrows():
        n = int(ch["video_count"])
        # Duration distribution: 30% short (<600s), 40% mid (600-2700s), 30% long (2700-4500s)
        n_short = max(1, int(n * 0.30))
        n_mid = max(1, int(n * 0.40))
        n_long = max(1, n - n_short - n_mid)
        durations = np.concatenate([
            RNG.integers(120, 600, size=n_short),
            RNG.integers(600, 2700, size=n_mid),
            RNG.integers(2700, 4500, size=n_long),
        ])[:n]
        # Pad if rounding left us short
        while len(durations) < n:
            durations = np.append(durations, RNG.integers(2700, 4500))
        RNG.shuffle(durations)
        views = RNG.integers(5_000, 2_000_000, size=n).astype(int)
        likes = (views * RNG.uniform(0.02, 0.08, size=n)).astype(int)
        days_ago = RNG.integers(1, 730, size=n)
        for i in range(n):
            rows.append({
                "video_id": f"VID{vid_id:05d}",
                "channel_id": ch["channel_id"],
                "title": f"{ch['channel_name']} — Video {vid_id}",
                "published_at": str(TODAY - timedelta(days=int(days_ago[i]))),
                "views": int(views[i]),
                "likes": int(likes[i]),
                "duration_seconds": int(durations[i]),
            })
            vid_id += 1
    return pd.DataFrame(rows)


def generate_growth(channels_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    months = pd.date_range(end=TODAY, periods=12, freq="MS")
    for _, ch in channels_df.iterrows():
        base_subs = ch["subscribers"]
        monthly_views_base = ch["total_views"] / 24  # ~2yr avg
        for i, month in enumerate(months):
            growth_factor = 1 + RNG.uniform(-0.02, 0.05)
            month_subs = int(base_subs * (0.88 + 0.01 * i) * growth_factor)
            month_views = int(monthly_views_base * RNG.uniform(0.80, 1.25))
            rows.append({
                "channel_id": ch["channel_id"],
                "month": str(month.date()),
                "subscriber_count": month_subs,
                "monthly_views": month_views,
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    channels = generate_channels()
    videos = generate_videos(channels)
    growth = generate_growth(channels)

    channels.to_csv(OUT_DIR / "channels.csv", index=False)
    videos.to_csv(OUT_DIR / "videos.csv", index=False)
    growth.to_csv(OUT_DIR / "growth.csv", index=False)

    print(f"channels.csv: {len(channels)} rows")
    print(f"videos.csv:   {len(videos)} rows")
    print(f"growth.csv:   {len(growth)} rows")
    print(f"Total subscribers in sample: {channels['subscribers'].sum():,}")
