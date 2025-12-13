from dataclasses import dataclass, field
from enum import Enum
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from rclpy.node import Node


class AcquisitionMode(Enum):
    """
    Acquisition mode for ZED 2i experiments.
    """
    FLIGHT = "flight"
    BENCH = "bench"
    RECONSTRUCTION = "reconstruction"


@dataclass
class ZedConfig:
    """
    ZED 2i configuration parameters.

    This class is intentionally simple and can be mapped to a C struct in a
    future implementation.
    """

    frame_rate: int = 15
    depth_min: float = 0.5
    depth_max: float = 20.0
    horizontal_fov_deg: float = 110.0
    vertical_fov_deg: float = 70.0
    ideal_distance_m: float = 12.0
    max_distance_m: float = 20.0
    altitude_m: float = 1.0

    point_cloud_topic: str = (
        "/zed/zed_node/point_cloud/cloud_registered"
    )
    left_image_topic: str = (
        "/zed/zed_node/left/image_rect_color"
    )
    right_image_topic: str = (
        "/zed/zed_node/right/image_rect_color"
    )

    extra_topics: List[str] = field(default_factory=list)
    storage_id: str = "mcap"

    @classmethod
    def from_parameters(cls, node: "Node") -> "ZedConfig":
        """
        Build a ZedConfig instance from ROS2 parameters.
        Default values are used if parameters are not set.

        :param node: rclpy Node used to declare and read parameters.
        :return: Configured ZedConfig instance.
        """
        frame_rate = node.declare_parameter(
            "frame_rate", cls.frame_rate
        ).value
        depth_min = node.declare_parameter(
            "depth_min", cls.depth_min
        ).value
        depth_max = node.declare_parameter(
            "depth_max", cls.depth_max
        ).value
        altitude_m = node.declare_parameter(
            "altitude_m", cls.altitude_m
        ).value

        point_cloud_topic = node.declare_parameter(
            "point_cloud_topic", cls.point_cloud_topic
        ).value
        left_image_topic = node.declare_parameter(
            "left_image_topic", cls.left_image_topic
        ).value
        right_image_topic = node.declare_parameter(
            "right_image_topic", cls.right_image_topic
        ).value

        # Use a non-empty default string array to avoid BYTE_ARRAY inference.
        # The YAML file will override this with a proper string array.
        default_extra_topics = [""]

        extra_topics_raw = node.declare_parameter(
            "extra_topics",
            default_extra_topics,
        ).value

        # Filter out empty strings, so the default effectively becomes [].
        extra_topics = [topic for topic in extra_topics_raw if topic]

        storage_id = node.declare_parameter(
            "storage_id", cls.storage_id
        ).value

        return cls(
            frame_rate=frame_rate,
            depth_min=depth_min,
            depth_max=depth_max,
            altitude_m=altitude_m,
            point_cloud_topic=point_cloud_topic,
            left_image_topic=left_image_topic,
            right_image_topic=right_image_topic,
            extra_topics=extra_topics,
            storage_id=storage_id,
        )
