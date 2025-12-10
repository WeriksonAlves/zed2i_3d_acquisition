import json
import datetime

from typing import Optional, List

from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, Image

from .config import ZedConfig, AcquisitionMode
from .rosbag_recorder import RosbagRecorder
from .utils.path_manager import ExperimentPathManager


class ZedPointCloudManager:
    """
    High-level manager for ZED 2i point cloud acquisition.

    Responsibilities:
    - Subscribe to ZED topics (point cloud and left image);
    - Manage ros2 bag recording through RosbagRecorder;
    - Expose hooks for future visualization or bench-mode processing.
    """

    def __init__(
        self,
        node: Node,
        config: ZedConfig,
        mode: AcquisitionMode,
        base_output_dir: str,
    ) -> None:
        self._node = node
        self._config = config
        self._mode = mode

        self._path_manager = ExperimentPathManager(base_dir=base_output_dir)
        self._experiment_dir = None

        self._rosbag_recorder: Optional[RosbagRecorder] = None

        self._point_cloud_subscription = None
        self._left_image_subscription = None

        self._latest_point_cloud: Optional[PointCloud2] = None
        self._latest_left_image: Optional[Image] = None

    def initialize_subscriptions(self) -> None:
        """
        Create ROS2 subscriptions for the ZED topics.
        """
        self._node.get_logger().info("Initializing ZED 2i subscriptions...")

        self._point_cloud_subscription = self._node.create_subscription(
            PointCloud2,
            self._config.point_cloud_topic,
            self._point_cloud_callback,
            10,
        )

        self._left_image_subscription = self._node.create_subscription(
            Image,
            self._config.left_image_topic,
            self._left_image_callback,
            10,
        )

    def _point_cloud_callback(self, msg: PointCloud2) -> None:
        """
        Store the latest point cloud message.
        """
        self._latest_point_cloud = msg

    def _left_image_callback(self, msg: Image) -> None:
        """
        Store the latest left image frame.
        """
        self._latest_left_image = msg
    
    def _write_experiment_metadata(
        self,
        experiment_name: str,
        topics: list[str],
    ) -> None:
        """
        Write a JSON file with experiment metadata, including sensor parameters
        and acquisition settings.
        """
        if self._experiment_dir is None:
            self._node.get_logger().warn(
                "Cannot write metadata: experiment directory is not set."
            )
            return

        metadata = {
            "sensor": {
                "name": "ZED 2i",
                "horizontal_fov_deg": self._config.horizontal_fov_deg,
                "vertical_fov_deg": self._config.vertical_fov_deg,
                "depth_min_m": self._config.depth_min,
                "depth_max_m": self._config.depth_max,
                "ideal_distance_m": self._config.ideal_distance_m,
                "max_distance_m": self._config.max_distance_m,
            },
            "experiment": {
                "name": experiment_name,
                "mode": self._mode.value,
                "altitude_m": self._config.altitude_m,
                "created_at": datetime.datetime.now().isoformat(),
            },
            "rosbag": {
                "topics": topics,
            },
        }

        metadata_path = self._experiment_dir / "experiment_metadata.json"

        try:
            with metadata_path.open("w", encoding="utf-8") as file:
                json.dump(metadata, file, indent=4)
            self._node.get_logger().info(
                f"Experiment metadata written to: {metadata_path}"
            )
        except OSError as exc:
            self._node.get_logger().error(
                f"Failed to write experiment metadata: {exc}"
            )

    def get_latest_point_cloud(self) -> Optional[PointCloud2]:
        """
        Get the most recent point cloud message received from the ZED.

        :return: Latest PointCloud2 message or None if no message arrived yet.
        """
        return self._latest_point_cloud

    def get_latest_left_image(self) -> Optional[Image]:
        """
        Get the most recent left image message received from the ZED.

        :return: Latest Image message or None if no message arrived yet.
        """
        return self._latest_left_image

    def start_recording(self, experiment_name: str) -> None:
        """
        Create an experiment directory and start ros2 bag recording.

        :param experiment_name: Logical experiment name, used to build
                                the output directory name.
        """
        self._experiment_dir = self._path_manager.create_experiment_dir(
            experiment_name=experiment_name
        )
        self._node.get_logger().info(
            f"Experiment directory created at: {self._experiment_dir}"
        )

        self._rosbag_recorder = RosbagRecorder(
            node=self._node,
            base_output_dir=str(self._experiment_dir),
        )

        topics: list[str] = [
            self._config.point_cloud_topic,
            self._config.left_image_topic,
        ] + list(self._config.extra_topics)

        # Write metadata before starting recording
        self._write_experiment_metadata(
            experiment_name=experiment_name,
            topics=topics,
        )

        bag_dir = self._rosbag_recorder.start_recording(
            bag_name="zed2i_recording",
            topics=topics,
        )

        self._node.get_logger().info(
            f"Recording ros2 bag in directory: {bag_dir}"
        )

    def stop_recording(self) -> None:
        """
        Stop the ros2 bag recording process if it is running.
        """
        if self._rosbag_recorder is None:
            self._node.get_logger().warn(
                "stop_recording() called but RosbagRecorder is not initialized."
            )
            return

        self._rosbag_recorder.stop_recording()

    def shutdown(self) -> None:
        """
        Clean shutdown of the point cloud manager.
        """
        self._node.get_logger().info("Shutting down ZedPointCloudManager...")
        self.stop_recording()

        # Subscriptions are attached to the node and will be destroyed when
        # the node is destroyed, so there is no need to unregister them here.
        self._point_cloud_subscription = None
        self._left_image_subscription = None

    # Placeholder for future bench visualization loop
    def run_bench_visualization_loop(self) -> None:
        """
        Placeholder for a future bench-mode visualization loop.
        This method can later integrate Open3D or RViz-based visualization.
        """
        self._node.get_logger().info(
            "Bench visualization loop is not implemented yet."
        )
