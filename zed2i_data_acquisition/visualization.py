"""
Utility functions for visualizing ZED 2i point clouds with Open3D.

This module is intentionally self-contained so it can be easily
ported or reimplemented in C in a later stage of the project.
"""

from typing import Tuple, Optional, List

import numpy as np
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2

try:
    import open3d as o3d

    _OPEN3D_AVAILABLE = True
except ImportError:
    o3d = None
    _OPEN3D_AVAILABLE = False


def _get_rgb_field_index(msg: PointCloud2, node=None) -> Optional[int]:
    """
    Get the index of the RGB/RGBA field in the PointCloud2 message.

    :param msg: PointCloud2 message.
    :param node: Optional rclpy node for logging.
    :return: Index of the RGB/RGBA field or None if not found.
    """
    field_names: List[str] = [field.name for field in msg.fields]

    if "rgb" in field_names:
        return field_names.index("rgb")
    if "rgba" in field_names:
        return field_names.index("rgba")

    if node is not None:
        node.get_logger().warn(
            "No 'rgb' or 'rgba' field found in PointCloud2. "
            "Colors will not be available."
        )
    return None


def pointcloud2_to_xyzrgb_array(
    msg: PointCloud2,
    node=None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert a PointCloud2 message to XYZ and RGB arrays.

    This function is robust to RGB/RGBA fields stored as float32 (packed)
    or as uint32 and to structured dtypes returned by sensor_msgs_py.
    The RGB values are returned normalized in [0, 1].

    :param msg: PointCloud2 message from the ZED 2i.
    :param node: Optional rclpy node for logging.
    :return: (xyz, rgb) arrays with shapes (N, 3) and (N, 3).
    """
    # Identify which color field is present
    field_names: List[str] = [field.name for field in msg.fields]
    if "rgb" in field_names:
        rgb_name = "rgb"
    elif "rgba" in field_names:
        rgb_name = "rgba"
    else:
        rgb_name = None

    # Case without color: only x, y, z
    if rgb_name is None:
        if node is not None:
            node.get_logger().warn(
                "No 'rgb' or 'rgba' field found in PointCloud2. "
                "Colors will not be available."
            )

        points_list = list(
            point_cloud2.read_points(
                msg,
                field_names=["x", "y", "z"],
                skip_nans=True,
            )
        )

        if len(points_list) == 0:
            return (
                np.empty((0, 3), dtype=np.float32),
                np.empty((0, 3), dtype=np.float32),
            )

        points = np.asarray(points_list)

        if points.ndim == 1:
            points = points.reshape(1, -1)

        xyz = points[:, 0:3].astype(np.float32)
        rgb = np.ones_like(xyz, dtype=np.float32)  # white points

        # Filter out non-finite points
        finite_mask = np.isfinite(xyz).all(axis=1)
        xyz = xyz[finite_mask]
        rgb = rgb[finite_mask]

        return xyz, rgb

    # Case with rgb/rgba: read x, y, z, rgb_name explicitly
    points_list = list(
        point_cloud2.read_points(
            msg,
            field_names=["x", "y", "z", rgb_name],
            skip_nans=True,
        )
    )

    if len(points_list) == 0:
        if node is not None:
            node.get_logger().warn(
                "Received empty PointCloud2 message. Nothing to visualize."
            )
        return (
            np.empty((0, 3), dtype=np.float32),
            np.empty((0, 3), dtype=np.float32),
        )

    points = np.asarray(points_list)

    # Structured array (dtype with field names)
    if points.dtype.names is not None:
        x = np.asarray(points["x"], dtype=np.float32)
        y = np.asarray(points["y"], dtype=np.float32)
        z = np.asarray(points["z"], dtype=np.float32)
        xyz = np.stack((x, y, z), axis=-1)

        rgb_raw = np.asarray(points[rgb_name])
    else:
        # Regular array
        if points.ndim == 1:
            points = points.reshape(1, -1)

        xyz = points[:, 0:3].astype(np.float32)
        rgb_raw = points[:, 3]

    # Convert color to uint32 before bit operations
    if np.issubdtype(rgb_raw.dtype, np.floating):
        rgb_as_float32 = rgb_raw.astype(np.float32, copy=False)
        rgb_uint32 = rgb_as_float32.view(np.uint32)
    else:
        rgb_uint32 = rgb_raw.astype(np.uint32, copy=False)

    r = (rgb_uint32 >> 16) & 0xFF
    g = (rgb_uint32 >> 8) & 0xFF
    b = rgb_uint32 & 0xFF

    rgb = np.stack([r, g, b], axis=-1).astype(np.float32) / 255.0

    # Filter out non-finite XYZ points (inf / NaN)
    finite_mask = np.isfinite(xyz).all(axis=1)
    xyz = xyz[finite_mask]
    rgb = rgb[finite_mask]

    if node is not None:
        node.get_logger().info(
            f"Filtered point cloud: kept {xyz.shape[0]} finite points "
            f"out of {len(points_list)} raw points."
        )

    return xyz, rgb


def pointcloud2_to_open3d(
    msg: PointCloud2,
    node=None,
) -> "o3d.geometry.PointCloud":
    """
    Convert a PointCloud2 message to an Open3D PointCloud.

    :param msg: PointCloud2 message.
    :param node: Optional rclpy node for logging.
    :return: Open3D PointCloud instance.
    :raises RuntimeError: If Open3D is not installed.
    """
    if not _OPEN3D_AVAILABLE:
        raise RuntimeError(
            "Open3D is not installed. Please install it with "
            "'pip install open3d' to enable visualization."
        )

    xyz, rgb = pointcloud2_to_xyzrgb_array(msg, node=node)

    pcd = o3d.geometry.PointCloud()
    if xyz.size > 0:
        pcd.points = o3d.utility.Vector3dVector(xyz)
        pcd.colors = o3d.utility.Vector3dVector(rgb)

    return pcd


def show_pointcloud_open3d(
    msg: PointCloud2,
    node=None,
    window_name: str = "ZED 2i Point Cloud",
    width: int = 1280,
    height: int = 720,
) -> None:
    """
    Visualize a PointCloud2 message in an Open3D window.

    :param msg: PointCloud2 message to visualize.
    :param node: Optional rclpy node for logging.
    :param window_name: Window name for the Open3D visualizer.
    :param width: Window width in pixels.
    :param height: Window height in pixels.
    """
    if not _OPEN3D_AVAILABLE:
        if node is not None:
            node.get_logger().error(
                "Open3D is not available. Please install it with "
                "'pip install open3d' to enable point cloud visualization."
            )
        return

    try:
        pcd = pointcloud2_to_open3d(msg, node=node)
    except RuntimeError as exc:
        if node is not None:
            node.get_logger().error(f"Failed to convert point cloud: {exc}")
        return

    num_points = len(pcd.points)
    if num_points == 0:
        if node is not None:
            node.get_logger().warn(
                "Point cloud has no valid points. Nothing will be displayed."
            )
        return

    # Debug: log basic statistics about the point cloud
    points_np = np.asarray(pcd.points)
    try:
        x_min, x_max = points_np[:, 0].min(), points_np[:, 0].max()
        y_min, y_max = points_np[:, 1].min(), points_np[:, 1].max()
        z_min, z_max = points_np[:, 2].min(), points_np[:, 2].max()
        if node is not None:
            node.get_logger().info(
                f"Open3D point cloud stats: N={num_points}, "
                f"x=[{x_min:.2f}, {x_max:.2f}], "
                f"y=[{y_min:.2f}, {y_max:.2f}], "
                f"z=[{z_min:.2f}, {z_max:.2f}]"
            )
    except Exception as exc:  # pragma: no cover - defensive
        if node is not None:
            node.get_logger().warn(
                f"Failed to compute point cloud stats: {exc}"
            )

    # Optional downsampling to avoid overloading the viewer
    # pcd = pcd.voxel_down_sample(voxel_size=0.05)

    # Use an explicit Visualizer to ensure the view is centered on the cloud
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=window_name, width=width, height=height)
    vis.add_geometry(pcd)

    # Center the view around the point cloud
    view_ctrl = vis.get_view_control()
    center = pcd.get_center()
    bounds = pcd.get_axis_aligned_bounding_box()
    extent = bounds.get_extent()
    max_extent = float(np.max(extent)) if extent is not None else 1.0

    # Simple, generic camera setup
    view_ctrl.set_lookat(center)
    view_ctrl.set_front([0.0, 0.0, -1.0])
    view_ctrl.set_up([0.0, -1.0, 0.0])
    # Zoom based on extent (avoid ficar "muito longe" ou "muito perto")
    if max_extent > 0:
        view_ctrl.set_zoom(0.7)

    vis.poll_events()
    vis.update_renderer()

    # This will block until the window is closed by the user
    vis.run()
    vis.destroy_window()
