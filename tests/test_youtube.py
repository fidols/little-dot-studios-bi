import pandas as pd
import pytest
from utils.youtube import (
    load_channels,
    load_videos,
    load_growth,
    avg_views_per_video,
    views_by_duration_bin,
    views_by_category,
)


def test_load_channels_returns_dataframe():
    df = load_channels()
    assert isinstance(df, pd.DataFrame)
    assert set(["channel_id", "channel_name", "subscribers", "total_views", "video_count", "category"]).issubset(df.columns)
    assert len(df) == 20


def test_load_videos_returns_dataframe():
    df = load_videos()
    assert isinstance(df, pd.DataFrame)
    assert "duration_seconds" in df.columns
    assert "views" in df.columns
    assert len(df) > 0


def test_load_growth_returns_dataframe():
    df = load_growth()
    assert isinstance(df, pd.DataFrame)
    assert "subscriber_count" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["month"])


def test_avg_views_per_video_correct():
    channels = pd.DataFrame([{"channel_id": "C1", "channel_name": "X", "subscribers": 1000,
                               "total_views": 5000, "video_count": 2, "category": "Sports"}])
    videos = pd.DataFrame([
        {"video_id": "V1", "channel_id": "C1", "title": "A", "published_at": "2026-01-01",
         "views": 1000, "likes": 50, "duration_seconds": 300},
        {"video_id": "V2", "channel_id": "C1", "title": "B", "published_at": "2026-02-01",
         "views": 3000, "likes": 120, "duration_seconds": 1800},
    ])
    result = avg_views_per_video(channels, videos)
    assert result == 2000.0


def test_views_by_duration_bin_bins_correctly():
    videos = pd.DataFrame([
        {"video_id": "V1", "channel_id": "C1", "title": "A", "published_at": "2026-01-01",
         "views": 100, "likes": 5, "duration_seconds": 300},   # < 10 min
        {"video_id": "V2", "channel_id": "C1", "title": "B", "published_at": "2026-01-01",
         "views": 200, "likes": 8, "duration_seconds": 1200},  # 10-30 min
        {"video_id": "V3", "channel_id": "C1", "title": "C", "published_at": "2026-01-01",
         "views": 300, "likes": 12, "duration_seconds": 2400}, # 30-45 min (40 min)
    ])
    result = views_by_duration_bin(videos)
    lt10 = result[result["duration_bin"] == "<10 min"]["avg_views"].values[0]
    mid = result[result["duration_bin"] == "10-30 min"]["avg_views"].values[0]
    assert lt10 == 100.0
    assert mid == 200.0


def test_views_by_category_sums_correctly():
    channels = pd.DataFrame([
        {"channel_id": "C1", "channel_name": "X", "subscribers": 1000,
         "total_views": 5000, "video_count": 1, "category": "Sports"},
        {"channel_id": "C2", "channel_name": "Y", "subscribers": 2000,
         "total_views": 8000, "video_count": 1, "category": "Documentary"},
    ])
    videos = pd.DataFrame([
        {"video_id": "V1", "channel_id": "C1", "title": "A", "published_at": "2026-01-01",
         "views": 500, "likes": 20, "duration_seconds": 300},
        {"video_id": "V2", "channel_id": "C2", "title": "B", "published_at": "2026-01-01",
         "views": 800, "likes": 30, "duration_seconds": 1200},
    ])
    result = views_by_category(channels, videos)
    sports = result[result["category"] == "Sports"]["total_views"].values[0]
    assert sports == 500


def test_views_by_duration_bin_empty_videos():
    videos = pd.DataFrame(columns=["video_id", "channel_id", "title", "published_at",
                                   "views", "likes", "duration_seconds"])
    result = views_by_duration_bin(videos)
    assert isinstance(result, pd.DataFrame)
