"""Tests for Track.with_noise() – random GPS offset generation."""

import math
import unittest
from datetime import datetime
from unittest.mock import patch

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
        """Metadata must be identical in the noisy copy."""
        original = _make_track(self.BASE_POINTS)
        noisy = original.with_noise()
        self.assertEqual(original.metadata, noisy.metadata)

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


class TestTrackWithRandomTime(unittest.TestCase):
    """Test cases for Track.with_random_time()."""

    BASE_POINTS = [
        (32.07393038666775, 118.77614938560684),
        (32.07411977632837, 118.77613914832789),
    ]

    def _make_track_local(self) -> Track:
        return _make_track(self.BASE_POINTS)

    def test_returns_new_track_instance(self):
        """with_random_time() should return a different Track object."""
        original = self._make_track_local()
        result = original.with_random_time(480, 720)
        self.assertIsNot(original, result)

    def test_total_time_within_range(self):
        """totalTime must be within [min_sec, max_sec]."""
        original = self._make_track_local()
        min_sec, max_sec = 300, 600
        for _ in range(20):
            result = original.with_random_time(min_sec, max_sec)
            self.assertGreaterEqual(result.metadata.totalTime, min_sec)
            self.assertLessEqual(result.metadata.totalTime, max_sec)

    def test_formatted_time_matches_total_time(self):
        """formattedTime must encode the same number of seconds as totalTime."""
        original = self._make_track_local()
        for _ in range(20):
            result = original.with_random_time(300, 720)
            total = result.metadata.totalTime
            expected = f"{total // 60} 分 {total % 60} 秒"
            self.assertEqual(result.metadata.formattedTime, expected)

    def test_other_metadata_fields_preserved(self):
        """All metadata fields other than totalTime/formattedTime must be unchanged."""
        original = self._make_track_local()
        result = original.with_random_time(480, 600)
        self.assertEqual(result.metadata.totalDistance, original.metadata.totalDistance)
        self.assertEqual(result.metadata.formattedDistance, original.metadata.formattedDistance)
        self.assertEqual(result.metadata.sampleTimeInterval, original.metadata.sampleTimeInterval)
        self.assertEqual(result.metadata.pointCount, original.metadata.pointCount)
        self.assertEqual(result.metadata.createdAt, original.metadata.createdAt)

    def test_track_points_preserved(self):
        """Track points must be unchanged."""
        original = self._make_track_local()
        result = original.with_random_time(480, 600)
        self.assertEqual(result.track, original.track)

    def test_original_track_unmodified(self):
        """with_random_time() must not mutate the original Track."""
        original = self._make_track_local()
        original_time = original.metadata.totalTime
        original.with_random_time(480, 600)
        self.assertEqual(original.metadata.totalTime, original_time)

    def test_two_calls_may_produce_different_times(self):
        """Repeated calls should occasionally produce different totalTime values."""
        original = self._make_track_local()
        times = {original.with_random_time(300, 720).metadata.totalTime for _ in range(50)}
        self.assertGreater(len(times), 1, "Expected at least two distinct random times in 50 calls")


if __name__ == "__main__":
    unittest.main()
