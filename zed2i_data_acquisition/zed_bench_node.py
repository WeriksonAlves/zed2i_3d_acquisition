import rclpy
from rclpy.node import Node

from .config import ZedConfig, AcquisitionMode
from .pointcloud_manager import ZedPointCloudManager
from .visualization import show_pointcloud_open3d


class ZedBenchNode(Node):
    """
    Node responsible for ZED 2i bench visualization and data inspection.

    It initializes the ZedPointCloudManager in BENCH mode and starts a timer
    that will trigger a one-shot visualization of the first received point
    cloud using Open3D (if installed).
    """

    def __init__(self) -> None:
        super().__init__("zed2i_bench_visualization")

        self.get_logger().info("ZED 2i Bench Node initializing...")

        # Load configuration from parameters
        self._config = ZedConfig.from_parameters(self)

        self._base_output_dir = self.declare_parameter(
            "base_output_dir", "/tmp/zed2i_bench_experiments"
        ).value

        self._manager = ZedPointCloudManager(
            node=self,
            config=self._config,
            mode=AcquisitionMode.BENCH,
            base_output_dir=self._base_output_dir,
        )

        self._manager.initialize_subscriptions()
        self.get_logger().info("ZED 2i Bench Node started.")

        # Timer for one-shot point cloud visualization
        self._visualization_done = False
        self._visualization_timer = self.create_timer(
            1.0,  # seconds
            self._visualization_timer_callback,
        )

    def _visualization_timer_callback(self) -> None:
        """
        Timer callback that tries to visualize the first received point cloud.

        This is a simple, bench-oriented visualization: as soon as a valid
        point cloud is available, we call Open3D to display it once and then
        stop the timer.
        """
        if self._visualization_done:
            return

        point_cloud = self._manager.get_latest_point_cloud()
        if point_cloud is None:
            self.get_logger().info(
                "Waiting for first point cloud from ZED 2i..."
            )
            return

        self.get_logger().info(
            "First point cloud received. Launching Open3D visualization..."
        )
        try:
            show_pointcloud_open3d(point_cloud, node=self)
            self._visualization_done = True
            self.destroy_timer(self._visualization_timer)
            self.get_logger().info(
                "Visualization finished. Timer disabled."
            )
        except RuntimeError as exc:
            # For example, if Open3D is not installed.
            self.get_logger().error(f"Visualization failed: {exc}")
            self._visualization_done = True
            self.destroy_timer(self._visualization_timer)

    def destroy_node(self) -> bool:
        """
        Ensure the manager is cleanly shutdown.
        """
        self.get_logger().info("Destroying ZED 2i Bench Node...")
        self._manager.shutdown()
        return super().destroy_node()


def main(args=None) -> None:
    """
    Entry point for the zed_bench_node console script.
    """
    rclpy.init(args=args)
    node = ZedBenchNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(
            "Keyboard interrupt received, shutting down ZED Bench Node."
        )
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()

