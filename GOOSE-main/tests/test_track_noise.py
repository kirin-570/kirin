"""Tests for Track.with_noise() – random GPS offset generation."""

import math
import unittest
from datetime import datetime
from unittest.mock import patch

from src.infrastructure.constants import TRACK_MAX_DURATION_SEC, TRACK_MIN_DURATION_SEC
from src.model.track import Track, TrackMetadata, TrackPoint

_FLOAT_TOLERANCE = 1e-9


def _make_track(points: list[tuple[float, float]]) -> Track:
    """Helper: build a Track from (lat, lng) tuples."""
    track_points = [
        TrackPoint(lat=lat, lng=lng, sortNum=i + 1) for i, (lat, lng) in enumerate(points)
    ]
    metadata = TrackMetadata(
        totalDistance=1000.0,
        formattedDistance="1.00 公里",
        totalTime=360,
        formattedTime="6 分 0 秒",
        sampleTimeInterval=8,
        pointCount=len(points),
        createdAt=datetime(2025, 1, 1),
    )
    return Track(track=track_points, metadata=metadata)


class TestTrackWithNoise(unittest.TestCase):
    """Test cases for Track.with_noise()."""

    BASE_POINTS = [
        (32.07393038666775, 118.77614938560684),
        (32.07411977632837, 118.77613914832789),
        (32.07430916598899, 118.77612891104894),
    ]

    def test_returns_new_track_instance(self):
        """with_noise() should return a different Track object."""
        original = _make_track(self.BASE_POINTS)
        noisy = original.with_noise()
        self.assertIsNot(original, noisy)

    def test_point_count_preserved(self):
        """Noisy track must have the same number of points as the original."""
        original = _make_track(self.BASE_POINTS)
        noisy = original.with_noise()
        self.assertEqual(len(noisy.track), len(original.track))

    def test_sort_nums_preserved(self):
        """sortNum values must be unchanged after adding noise."""
        original = _make_track(self.BASE_POINTS)
        noisy = original.with_noise()
        for orig_pt, noisy_pt in zip(original.track, noisy.track):
            self.assertEqual(orig_pt.sortNum, noisy_pt.sortNum)

    def test_metadata_preserved(self):
        """Non-time metadata fields must be identical in the noisy copy."""
        original = _make_track(self.BASE_POINTS)
        noisy = original.with_noise()
        original_meta = original.metadata.model_dump(exclude={"totalTime", "formattedTime"})
        noisy_meta = noisy.metadata.model_dump(exclude={"totalTime", "formattedTime"})
        self.assertEqual(original_meta, noisy_meta)

    def test_duration_within_range(self):
        """with_noise() must produce a totalTime within the configured 9–11 minute range."""
        original = _make_track(self.BASE_POINTS)
        for _ in range(100):
            noisy = original.with_noise()
            self.assertGreaterEqual(noisy.metadata.totalTime, TRACK_MIN_DURATION_SEC)
            self.assertLessEqual(noisy.metadata.totalTime, TRACK_MAX_DURATION_SEC)

    def test_formatted_time_matches_total_time(self):
        """formattedTime must reflect the randomised totalTime."""
        original = _make_track(self.BASE_POINTS)
        noisy = original.with_noise()
        expected = f"{noisy.metadata.totalTime // 60} 分 {noisy.metadata.totalTime % 60} 秒"
        self.assertEqual(noisy.metadata.formattedTime, expected)

    def test_offset_within_max_bounds(self):
        """Each noisy point must be within max_offset_m metres of the original."""
        max_offset_m = 4.0
        original = _make_track(self.BASE_POINTS)
        noisy = original.with_noise(max_offset_m=max_offset_m)

        for orig_pt, noisy_pt in zip(original.track, noisy.track):
            dist_km = orig_pt.distance_with(noisy_pt)
            dist_m = dist_km * 1000
            # Diagonal of a square with sides max_offset_m is max_offset_m * sqrt(2)
            self.assertLessEqual(
                dist_m,
                max_offset_m * math.sqrt(2) + _FLOAT_TOLERANCE,
                msg=f"Point displaced {dist_m:.4f} m, expected ≤ {max_offset_m * math.sqrt(2):.4f} m",
            )

    def test_two_calls_produce_different_tracks(self):
        """Two successive calls should produce different coordinate sets."""
        original = _make_track(self.BASE_POINTS)
        noisy1 = original.with_noise()
        noisy2 = original.with_noise()

        coords1 = [(p.lat, p.lng) for p in noisy1.track]
        coords2 = [(p.lat, p.lng) for p in noisy2.track]
        self.assertNotEqual(
            coords1,
            coords2,
            "Two calls to with_noise() should produce different coordinates",
        )

    def test_original_track_unmodified(self):
        """with_noise() must not mutate the original Track."""
        original = _make_track(self.BASE_POINTS)
        original_coords = [(p.lat, p.lng) for p in original.track]
        original.with_noise()
        after_coords = [(p.lat, p.lng) for p in original.track]
        self.assertEqual(original_coords, after_coords)

    def test_zero_offset_returns_identical_coordinates(self):
        """with_noise(max_offset_m=0) should leave all coordinates unchanged."""
        original = _make_track(self.BASE_POINTS)
        with patch("random.uniform", return_value=0.0):
            noisy = original.with_noise(max_offset_m=0.0)
        for orig_pt, noisy_pt in zip(original.track, noisy.track):
            self.assertAlmostEqual(orig_pt.lat, noisy_pt.lat, places=12)
            self.assertAlmostEqual(orig_pt.lng, noisy_pt.lng, places=12)

    def test_custom_max_offset(self):
        """with_noise respects a custom max_offset_m value."""
        max_offset_m = 2.0
        original = _make_track(self.BASE_POINTS)
        noisy = original.with_noise(max_offset_m=max_offset_m)

        for orig_pt, noisy_pt in zip(original.track, noisy.track):
            dist_m = orig_pt.distance_with(noisy_pt) * 1000
            self.assertLessEqual(dist_m, max_offset_m * math.sqrt(2) + _FLOAT_TOLERANCE)


if __name__ == "__main__":
    unittest.main()
