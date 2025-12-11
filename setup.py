from setuptools import setup

package_name = "zed2i_data_acquisition"

setup(
    name=package_name,
    version="0.0.0",
    packages=[
        package_name,
        f"{package_name}.utils",
    ],
    data_files=[
        # Ament index resource
        (
            "share/ament_index/resource_index/packages",
            [f"resource/{package_name}"],
        ),
        # Package manifest + root docs
        (
            f"share/{package_name}",
            [
                "package.xml",
            ],
        ),
        # Launch files
        (
            f"share/{package_name}/launch",
            [
                "launch/zed_flight_record.launch.py",
                "launch/zed_flight_record.launch",
                "launch/zed_bench_visualization.launch",
                "launch/zed_full_pipeline.launch",
            ],
        ),
        # Config files
        (
            f"share/{package_name}/config",
            [
                "config/zed_flight_config.yaml",
                "config/zed_bench_config.yaml",
                "config/topics.yaml",
            ],
        ),
        # Extra docs
        (
            f"share/{package_name}/docs",
            [
                "docs/design_overview.md",
                "docs/experiment_protocol.md",
                "docs/sensor_parameters.md",
            ],
        ),
    ],
    install_requires=[
        "setuptools",
        # "open3d",  # opcional, você instala via pip/venv se quiser
    ],
    zip_safe=True,
    maintainer="werikson",
    maintainer_email='werikson.alves@ufv.br',
    description="ZED 2i point cloud acquisition and ros2 bag recording tools.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "zed_flight_node = zed2i_data_acquisition.zed_flight_node:main",
            "zed_bench_node = zed2i_data_acquisition.zed_bench_node:main",
        ],
    },
)
