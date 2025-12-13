import pathlib
import signal
import subprocess
import threading
from typing import List, Optional

from rclpy.node import Node


class RosbagRecorder:
    """
    Start and stop a `ros2 bag record` subprocess.

    Notes:
    - Uses the ROS 2 CLI to keep the recording logic simple and portable.
    - Supports selecting a rosbag2 storage plugin (e.g., "mcap", "sqlite3").
    """

    def __init__(
        self,
        node: Node,
        base_output_dir: str,
        storage_id: str = "mcap",
    ) -> None:
        if not storage_id or not storage_id.strip():
            raise ValueError("storage_id must be a non-empty string.")

        self._node = node
        self._storage_id = storage_id.strip()

        self._base_output_dir = pathlib.Path(base_output_dir)
        self._base_output_dir.mkdir(parents=True, exist_ok=True)

        self._process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._current_bag_dir: Optional[pathlib.Path] = None

    def start_recording(self, bag_name: str, topics: List[str]
                        ) -> pathlib.Path:
        """
        Start recording the specified topics into a bag directory.

        `ros2 bag record -o <bag_name> ...` creates a directory named
        <bag_name> inside the current working directory (cwd).

        :param bag_name: Bag output directory name.
        :param topics: List of ROS topic names to record.
        :return: Full path to the bag directory being recorded.
        """
        bag_name = bag_name.strip()
        if not bag_name:
            raise ValueError("bag_name must be a non-empty string.")

        if not topics:
            raise ValueError("topics must be a non-empty list of topic names.")

        with self._lock:
            if self._process is not None:
                self._node.get_logger().warn(
                    "RosbagRecorder is already recording."
                )
                return self._current_bag_dir or self._base_output_dir

            self._current_bag_dir = self._base_output_dir / bag_name

            cmd = [
                "ros2",
                "bag",
                "record",
                "--storage",
                self._storage_id,
                "-o",
                bag_name,
                *topics,
            ]

            self._node.get_logger().info(
                f"Starting ros2 bag record in '{self._base_output_dir}' "
                f"with command: {' '.join(cmd)}"
            )

            # Use PIPE only if you plan to read output; otherwise inherit
            # stdout/stderr
            self._process = subprocess.Popen(
                cmd,
                cwd=str(self._base_output_dir),
            )

            return self._current_bag_dir

    def stop_recording(self) -> None:
        """
        Stop the recording subprocess if it is running.

        Uses SIGINT to mimic Ctrl+C, which is the clean shutdown path for
        rosbag2.
        """
        with self._lock:
            if self._process is None:
                self._node.get_logger().warn(
                    "RosbagRecorder.stop_recording() called, but no "
                    "recording process is running."
                )
                return

            self._node.get_logger().info(
                "Stopping ros2 bag recording process..."
            )

            # Prefer SIGINT for clean rosbag shutdown
            try:
                self._process.send_signal(signal.SIGINT)
            except OSError as exc:
                self._node.get_logger().warn(
                    "Failed to send SIGINT to rosbag process: %s. "
                    "Falling back to terminate().",
                    str(exc),
                )
                self._process.terminate()

            return_code = self._process.wait()
            self._node.get_logger().info(
                f"ros2 bag record process exited with code: {return_code}"
            )

            self._process = None
            self._current_bag_dir = None

    def get_current_bag_dir(self) -> Optional[pathlib.Path]:
        """
        Get the directory of the bag currently being recorded.
        """
        return self._current_bag_dir
