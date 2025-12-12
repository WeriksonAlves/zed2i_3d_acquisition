import rclpy
from rclpy.node import Node

from .config import ZedConfig, AcquisitionMode
from .pointcloud_manager import ZedPointCloudManager


class ZedFlightNode(Node):
    """
    Node responsible for ZED 2i flight acquisition.

    It delegates data handling and rosbag recording logic to ZedPointCloudManager,
    keeping this node focused on ROS2 integration.
    """

    def __init__(self) -> None:
        super().__init__("zed2i_flight_acquisition")

        self.get_logger().info("ZED 2i Flight Node initializing...")

        self._config = ZedConfig.from_parameters(self)

        self._experiment_name = self.declare_parameter(
            "experiment_name", "flight_experiment"
        ).value

        self._base_output_dir = self.declare_parameter(
            "base_output_dir", "/tmp/zed2i_flight_experiments"
        ).value

        self._manager = ZedPointCloudManager(
            node=self,
            config=self._config,
            mode=AcquisitionMode.FLIGHT,
            base_output_dir=self._base_output_dir,
        )

        self._manager.initialize_subscriptions()
        self._manager.start_recording(experiment_name=self._experiment_name)

        self.get_logger().info("ZED 2i Flight Node started.")

    def shutdown(self) -> None:
        """
        Perform a clean shutdown of the node resources.

        This must be called before destroy_node() and before rclpy.shutdown().
        """
        if rclpy.ok():
            self.get_logger().info("Shutting down ZED 2i Flight Node...")

        self._manager.shutdown()


def main(args=None) -> None:
    """
    Entry point for the zed_flight_node console script.
    """
    rclpy.init(args=args)
    node = ZedFlightNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        if rclpy.ok():
            node.get_logger().info(
                "Keyboard interrupt received, shutting down ZED Flight Node."
            )
    finally:
        # Cleanup while ROS context is still valid
        try:
            node.shutdown()
        except Exception as exc:
            # Avoid ROS logging here; context might be shutting down.
            print(f"[zed2i_flight_acquisition] Shutdown error: {exc}")

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()

