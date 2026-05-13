import pandas as pd
from pathlib import Path

_YOUTUBE_DIR = Path(__file__).parent.parent / "data" / "youtube"


def load_channels() -> pd.DataFrame:
    """Load channels.csv. Columns: channel_id, channel_name, subscribers, total_views, video_count, category."""
    return pd.read_csv(_YOUTUBE_DIR / "channels.csv")


def load_videos() -> pd.DataFrame:
    """Load videos.csv. Parses published_at as datetime."""
    df = pd.read_csv(_YOUTUBE_DIR / "videos.csv")
    df["published_at"] = pd.to_datetime(df["published_at"])
    return df


def load_growth() -> pd.DataFrame:
    """Load growth.csv. Parses month as datetime."""
    df = pd.read_csv(_YOUTUBE_DIR / "growth.csv")
    df["month"] = pd.to_datetime(df["month"])
    return df


def avg_views_per_video(channels_df: pd.DataFrame, videos_df: pd.DataFrame) -> float:
    """Mean views per video across all loaded videos."""
    if videos_df.empty:
        return 0.0
    return float(videos_df["views"].mean())


def views_by_duration_bin(videos_df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups videos into duration bins and returns avg views per bin.
    Bins: <10 min, 10-30 min, 30-45 min, 45-60 min, 60+ min
    Returns DataFrame with columns: duration_bin, avg_views.
    """
    if videos_df.empty:
        return pd.DataFrame(columns=["duration_bin", "avg_views"])
    df = videos_df.copy()
    df["duration_minutes"] = df["duration_seconds"] / 60
    bins = [0, 10, 30, 45, 60, float("inf")]
    labels = ["<10 min", "10-30 min", "30-45 min", "45-60 min", "60+ min"]
    df["duration_bin"] = pd.cut(df["duration_minutes"], bins=bins, labels=labels, right=False)
    return (
        df.groupby("duration_bin", observed=True)["views"]
        .mean()
        .reset_index()
        .rename(columns={"views": "avg_views"})
    )


def views_by_category(channels_df: pd.DataFrame, videos_df: pd.DataFrame) -> pd.DataFrame:
    """Total views by channel category. Joins videos with channels on channel_id."""
    merged = videos_df.merge(channels_df[["channel_id", "category"]], on="channel_id", how="left")
    return (
        merged.groupby("category")["views"]
        .sum()
        .reset_index()
        .rename(columns={"views": "total_views"})
    )
