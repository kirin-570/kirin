import math
import unittest
from datetime import datetime

from src.model.track import Track, TrackMetadata, TrackPoint


def _make_track(points: list[tuple[float, float]]) -> Track:
    """构造包含指定经纬度列表的 Track 对象，用于测试。"""
    track_points = [
        TrackPoint(lat=lat, lng=lng, sortNum=i + 1) for i, (lat, lng) in enumerate(points)
    ]
    metadata = TrackMetadata(
        totalDistance=1000.0,
        formattedDistance="1.00 公里",
        totalTime=300,
        formattedTime="5 分",
        sampleTimeInterval=10,
        pointCount=len(track_points),
        createdAt=datetime(2025, 1, 1),
    )
    return Track(track=track_points, metadata=metadata)


class TestTrackApplyNoise(unittest.TestCase):
    """测试 Track.apply_noise() 方法"""

    BASE_POINTS = [
        (32.0, 118.8),
        (32.001, 118.801),
        (32.002, 118.802),
    ]

    def test_apply_noise_returns_new_track(self):
        """apply_noise 应返回新的 Track 对象，而不修改原对象"""
        original = _make_track(self.BASE_POINTS)
        noisy = original.apply_noise()

        self.assertIsNot(original, noisy)
        # 原始轨迹点保持不变
        for orig_pt, base_pt in zip(original.track, self.BASE_POINTS):
            self.assertAlmostEqual(orig_pt.lat, base_pt[0])
            self.assertAlmostEqual(orig_pt.lng, base_pt[1])

    def test_apply_noise_preserves_point_count(self):
        """apply_noise 应保持轨迹点数量不变"""
        original = _make_track(self.BASE_POINTS)
        noisy = original.apply_noise()

        self.assertEqual(len(noisy.track), len(original.track))

    def test_apply_noise_preserves_sort_num(self):
        """apply_noise 应保持每个轨迹点的 sortNum 不变"""
        original = _make_track(self.BASE_POINTS)
        noisy = original.apply_noise()

        for orig_pt, noisy_pt in zip(original.track, noisy.track):
            self.assertEqual(orig_pt.sortNum, noisy_pt.sortNum)

    def test_apply_noise_preserves_metadata(self):
        """apply_noise 应保持轨迹元数据不变"""
        original = _make_track(self.BASE_POINTS)
        noisy = original.apply_noise()

        self.assertEqual(noisy.metadata, original.metadata)

    def test_apply_noise_offset_within_max_meters(self):
        """每个轨迹点的偏移量应在 max_meters 范围内"""
        original = _make_track(self.BASE_POINTS)
        max_meters = 5.0
        noisy = original.apply_noise(max_meters=max_meters)

        earth_radius_km = 6378.13649
        meters_per_degree_lat = earth_radius_km * 1000 * math.pi / 180

        for orig_pt, noisy_pt in zip(original.track, noisy.track):
            lat_offset_deg = abs(noisy_pt.lat - orig_pt.lat)
            lng_offset_deg = abs(noisy_pt.lng - orig_pt.lng)

            lat_offset_m = lat_offset_deg * meters_per_degree_lat
            meters_per_degree_lng = meters_per_degree_lat * math.cos(math.radians(orig_pt.lat))
            lng_offset_m = lng_offset_deg * meters_per_degree_lng

            self.assertLessEqual(lat_offset_m, max_meters + 1e-9)
            self.assertLessEqual(lng_offset_m, max_meters + 1e-9)

    def test_apply_noise_produces_different_results_each_call(self):
        """每次调用 apply_noise 应产生不同的结果（高概率）"""
        original = _make_track(self.BASE_POINTS)
        noisy1 = original.apply_noise()
        noisy2 = original.apply_noise()

        # 两次噪声结果中至少有一个点不同（两次恰好相同的概率极低）
        diffs = [
            (n1.lat != n2.lat or n1.lng != n2.lng)
            for n1, n2 in zip(noisy1.track, noisy2.track)
        ]
        self.assertTrue(any(diffs), "两次噪声结果完全相同，随机性异常")

    def test_apply_noise_points_differ_from_original(self):
        """噪声后的轨迹点应与原始点不同（高概率）"""
        original = _make_track(self.BASE_POINTS)
        noisy = original.apply_noise()

        diffs = [
            (n.lat != o.lat or n.lng != o.lng)
            for n, o in zip(noisy.track, original.track)
        ]
        self.assertTrue(any(diffs), "噪声结果与原始轨迹完全相同，随机性异常")

    def test_apply_noise_empty_track(self):
        """空轨迹的 apply_noise 应返回空轨迹"""
        original = _make_track([])
        noisy = original.apply_noise()

        self.assertEqual(len(noisy.track), 0)

    def test_apply_noise_single_point(self):
        """单点轨迹的 apply_noise 应正常工作"""
        original = _make_track([(32.0, 118.8)])
        noisy = original.apply_noise()

        self.assertEqual(len(noisy.track), 1)
        self.assertEqual(noisy.track[0].sortNum, 1)


if __name__ == "__main__":
    unittest.main()
