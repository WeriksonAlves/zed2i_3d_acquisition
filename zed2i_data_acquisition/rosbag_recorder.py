import pathlib
import subprocess
import threading
from typing import List, Optional

from rclpy.node import Node


class RosbagRecorder:
    """
    Responsible for starting and stopping a ros2 bag record process.

    This class uses the CLI `ros2 bag record` with subprocess, which makes it
    easy to port the high-level logic to another language.
    """

    def __init__(self, node: Node, base_output_dir: str) -> None:
        self._node = node
        self._base_output_dir = pathlib.Path(base_output_dir)
        self._base_output_dir.mkdir(parents=True, exist_ok=True)

        self._process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._current_bag_dir: Optional[pathlib.Path] = None

    def start_recording(self, bag_name: str, topics: List[str]) -> pathlib.Path:
        """
        Start ros2 bag recording for the specified topics.

        A directory named <bag_name> will be created inside base_output_dir.

        :param bag_name: Base name for the bag directory.
        :param topics: List of ROS topic names to record.
        :return: Full path to the bag directory being recorded.
        """
        with self._lock:
            if self._process is not None:
                self._node.get_logger().warn(
                    "RosbagRecorder is already recording."
                )
                return self._current_bag_dir or self._base_output_dir

            self._current_bag_dir = self._base_output_dir / bag_name

            # `ros2 bag record -o <bag_name> <topics...>` creates a directory
            # called <bag_name> in the current working directory.
            cmd = ["ros2", "bag", "record", "-o", bag_name] + topics

            self._node.get_logger().info(
                f"Starting ros2 bag record in {self._base_output_dir} "
                f"with command: {' '.join(cmd)}"
            )

            self._process = subprocess.Popen(
                cmd,
                cwd=str(self._base_output_dir),
            )

            return self._current_bag_dir

    def stop_recording(self) -> None:
        """
        Stop the ros2 bag recording process if it is running.
        """
        with self._lock:
            if self._process is None:
                self._node.get_logger().warn(
                    "RosbagRecorder.stop_recording() called, but no "
                    "recording process is running."
                )
                return

            self._node.get_logger().info("Stopping ros2 bag recording process.")
            # SIGINT is usually the cleanest way to stop ros2 bag.
            self._process.terminate()
            self._process.wait()
            self._process = None
            self._current_bag_dir = None

    def get_current_bag_dir(self) -> Optional[pathlib.Path]:
        """
        Get the directory of the bag that is currently being recorded.
        """
        return self._current_bag_dir
