from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description() -> LaunchDescription:
    """
    Launch ZED 2i flight acquisition node with parameters from YAML.
    """

    package_name = "zed2i_data_acquisition"
    config_file = os.path.join(
        get_package_share_directory(package_name),
        "config",
        "zed_flight_config.yaml",
    )

    experiment_name_arg = DeclareLaunchArgument(
        "experiment_name",
        default_value="flight_experiment",
        description="Logical name for this flight experiment.",
    )

    base_output_dir_arg = DeclareLaunchArgument(
        "base_output_dir",
        default_value="/tmp/zed2i_flight_experiments",
        description="Base directory for flight experiment outputs.",
    )

    experiment_name = LaunchConfiguration("experiment_name")
    base_output_dir = LaunchConfiguration("base_output_dir")

    zed_flight_node = Node(
        package=package_name,
        executable="zed_flight_node",
        name="zed2i_flight_acquisition",
        output="screen",
        parameters=[
            config_file,
            {
                "experiment_name": ParameterValue(experiment_name, value_type=str),
                "base_output_dir": ParameterValue(
                    base_output_dir, value_type=str
                ),
            },
        ],
    )

    return LaunchDescription(
        [
            experiment_name_arg,
            base_output_dir_arg,
            zed_flight_node,
        ]
    )
