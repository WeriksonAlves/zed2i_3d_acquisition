from __future__ import annotations

from typing import Optional, Iterable, Tuple

import numpy as np
from sensor_msgs.msg import PointCloud2

from rclpy.node import Node

try:
    import open3d as o3d
except ImportError:  # pragma: no cover - optional dependency
    o3d = None


def pointcloud2_to_xyzrgb_array(
    point_cloud: PointCloud2,
    node: Optional[Node] = None,
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Convert a ROS2 PointCloud2 message to NumPy arrays (XYZ and optional RGB).

    :param point_cloud: Input PointCloud2 message.
    :param node: Optional ROS2 node for logging.
    :return: Tuple (xyz, rgb) where:
             - xyz is an (N, 3) float32 array;
             - rgb is an (N, 3) uint8 array or None if not available.
    """
    # Import here to avoid hard dependency at import time.
    from sensor_msgs_py import point_cloud2

    field_names = [field.name for field in point_cloud.fields]
    has_rgb = "rgb" in field_names or "rgba" in field_names

    points_iter: Iterable = point_cloud2.read_points(
        point_cloud,
        field_names=field_names,
        skip_nans=True,
    )

    xyz_list = []
    rgb_list = []

    for p in points_iter:
        x, y, z = p[0], p[1], p[2]
        xyz_list.append([x, y, z])

        if has_rgb:
            # The rgb field may be stored as float32 packing the 3 channels.
            # This is a common pattern in PCL/ROS.
            rgb_packed = p[field_names.index("rgb")]  # type: ignore[index]
            if isinstance(rgb_packed, float):
                rgb_int = int(rgb_packed)
            else:
                rgb_int = rgb_packed

            r = (rgb_int >> 16) & 0xFF
            g = (rgb_int >> 8) & 0xFF
            b = rgb_int & 0xFF
            rgb_list.append([r, g, b])

    xyz = np.asarray(xyz_list, dtype=np.float32)
    rgb = np.asarray(rgb_list, dtype=np.uint8) if has_rgb else None

    if node is not None:
        node.get_logger().info(
            f"Converted PointCloud2 to arrays: xyz shape={xyz.shape}, "
            f"has_rgb={has_rgb}"
        )

    return xyz, rgb


def pointcloud2_to_open3d(
    point_cloud: PointCloud2,
    node: Optional[Node] = None,
) -> "o3d.geometry.PointCloud":
    """
    Convert a PointCloud2 message to an Open3D PointCloud.

    :param point_cloud: Input PointCloud2 message.
    :param node: Optional ROS2 node for logging.
    :return: Open3D PointCloud instance.
    :raises RuntimeError: If Open3D is not installed.
    """
    if o3d is None:
        raise RuntimeError(
            "Open3D is not installed. Please install it to use visualization."
        )

    xyz, rgb = pointcloud2_to_xyzrgb_array(point_cloud, node=node)

    pcd = o3d.geometry.PointCloud()
    if xyz.size > 0:
        pcd.points = o3d.utility.Vector3dVector(xyz)

    if rgb is not None and rgb.size > 0:
        # Normalize to [0, 1] for Open3D
        rgb_float = (rgb.astype(np.float32) / 255.0).reshape(-1, 3)
        pcd.colors = o3d.utility.Vector3dVector(rgb_float)

    if node is not None:
        node.get_logger().info(
            f"Created Open3D PointCloud with {len(pcd.points)} points."
        )

    return pcd


def show_pointcloud_open3d(
    point_cloud: PointCloud2,
    node: Optional[Node] = None,
) -> None:
    """
    Convenience function: convert PointCloud2 message to Open3D and show it.

    This is intended for bench testing and quick visual inspection, not for
    real-time visualization.

    :param point_cloud: Input PointCloud2 message.
    :param node: Optional ROS2 node for logging.
    """
    if o3d is None:
        if node is not None:
            node.get_logger().error(
                "Open3D is not installed. Cannot show point cloud."
            )
        return

    pcd = pointcloud2_to_open3d(point_cloud, node=node)
    if len(pcd.points) == 0:
        if node is not None:
            node.get_logger().warn(
                "Point cloud is empty. Skipping visualization."
            )
        return

    if node is not None:
        node.get_logger().info(
            "Opening Open3D window for point cloud visualization."
        )

    o3d.visualization.draw_geometries([pcd])
