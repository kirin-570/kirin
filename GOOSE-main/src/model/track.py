import json
import math
import random
from datetime import datetime

from pydantic import BaseModel

from src.infrastructure.constants import (
    EARTH_RADIUS_KM,
    METERS_PER_DEGREE_LATITUDE,
    TRACK_MAX_DURATION_SEC,
    TRACK_MIN_DURATION_SEC,
)


class TrackMetadata(BaseModel):
    """
    轨迹元数据模型

    包含轨迹的统计信息和元数据。
    """

    totalDistance: float  # 总距离（米）
    formattedDistance: str  # 格式化的距离字符串
    totalTime: int  # 总时间（秒）
    formattedTime: str  # 格式化的时间字符串
    sampleTimeInterval: int  # 采样时间间隔（秒）
    pointCount: int  # 轨迹点数量
    createdAt: datetime  # 创建时间


class TrackPoint(BaseModel):
    """
    单个经纬度轨迹点

    表示运动轨迹上的一个地理位置点。
    """

    lat: float  # 纬度
    lng: float  # 经度
    sortNum: int  # 排序号

    def distance_with(self, other: "TrackPoint") -> float:
        """
        计算两个轨迹点之间的距离

        使用Haversine公式计算地球上两经纬度点之间的球面距离。

        Args:
            other: 另一个轨迹点

        Returns:
            两点之间的距离（公里）
        """
        rad_lat1 = math.radians(self.lat)
        rad_lat2 = math.radians(other.lat)
        l1 = rad_lat1 - rad_lat2
        l2 = math.radians(self.lng) - math.radians(other.lng)
        haversine = math.pow(math.sin(l1 / 2), 2) + math.cos(rad_lat1) * math.cos(
            rad_lat2
        ) * math.pow(math.sin(l2 / 2), 2)
        angular_distance = 2 * math.asin(math.sqrt(haversine))
        d = angular_distance * EARTH_RADIUS_KM
        return d


class Track(BaseModel):
    """
    运动轨迹数据模型

    包含完整的轨迹点列表和元数据，提供距离计算等功能。
    """

    track: list[TrackPoint]  # 轨迹点列表
    metadata: TrackMetadata  # 轨迹元数据

    def get_distance_km(self) -> float:
        """
        计算轨迹的总距离

        通过累加相邻轨迹点之间的距离来计算总距离。

        Returns:
            总距离（公里）
        """
        distance = 0.0
        for p1, p2 in zip(self.track[:-1], self.track[1:]):
            distance += p1.distance_with(p2)

        return distance

    def get_track_str(self) -> str:
        """
        获取轨迹的JSON字符串表示

        Returns:
            轨迹点列表的JSON字符串
        """
        return json.dumps(self.model_dump()["track"])

    def get_duration_sec(self) -> int:
        """
        获取轨迹的持续时间

        Returns:
            持续时间（秒）
        """
        return self.metadata.totalTime

    def with_noise(self, max_offset_m: float = 4.0) -> "Track":
        """
        生成带有随机噪声的新轨迹副本

        为每个轨迹点在纬度和经度方向分别添加 [-max_offset_m, max_offset_m]
        范围内的随机偏移，使每次生成的路径独一无二。

        Args:
            max_offset_m: 每个方向的最大偏移量（米），默认4米

        Returns:
            带有随机偏移的新轨迹
        """
        # 1度纬度约等于111320米
        lat_m_per_deg = METERS_PER_DEGREE_LATITUDE

        noisy_points = []
        for point in self.track:
            # 经度的米/度比率取决于当前纬度
            lng_m_per_deg = METERS_PER_DEGREE_LATITUDE * math.cos(math.radians(point.lat))

            lat_offset = random.uniform(-max_offset_m, max_offset_m) / lat_m_per_deg
            lng_offset = random.uniform(-max_offset_m, max_offset_m) / lng_m_per_deg

            noisy_points.append(
                TrackPoint(
                    lat=point.lat + lat_offset,
                    lng=point.lng + lng_offset,
                    sortNum=point.sortNum,
                )
            )

        total_time = random.randint(TRACK_MIN_DURATION_SEC, TRACK_MAX_DURATION_SEC)
        formatted_time = f"{total_time // 60} 分 {total_time % 60} 秒"
        noisy_metadata = self.metadata.model_copy(
            update={"totalTime": total_time, "formattedTime": formatted_time}
        )
        return Track(track=noisy_points, metadata=noisy_metadata)
