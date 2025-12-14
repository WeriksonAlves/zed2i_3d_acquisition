from setuptools import setup, find_packages
from glob import glob
import os

package_name = "zed2i_data_acquisition"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test", "tests"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        # Install launch files (support both ROS2 *.launch.py and legacy *.launch)
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py") + glob("launch/*.launch")),
        # Install config files
        (os.path.join("share", package_name, "config"), glob("config/*.yaml") + glob("config/*.yml")),
        # Optional docs
        (os.path.join("share", package_name, "docs"), glob("docs/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="werikson",
    maintainer_email="werikson.alves@ufv.br",
    description="ZED 2i point cloud acquisition and ros2 bag recording tools.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "zed_flight_node = zed2i_data_acquisition.zed_flight_node:main",
            "zed_bench_node = zed2i_data_acquisition.zed_bench_node:main",
            "zed_reconstruction_node = zed2i_data_acquisition.zed_reconstruction_node:main",
        ],
    },
)
