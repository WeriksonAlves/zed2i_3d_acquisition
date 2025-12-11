# ZED2i 3D Acquisition

**Modular ROS 2 Framework for Point Cloud Acquisition, Recording and Visualization using the Stereolabs ZED 2i Stereo Camera**

This repository provides a **robust and extensible ROS 2 Humble framework** for 3D perception using the **ZED 2i stereo camera**, enabling:

* High-fidelity **point cloud acquisition**
* Automated **rosbag recording pipelines**
* Real-time **bench visualization with Open3D**
* Structured **flight experiment logging**
* Clean modular architecture following **PEP8**, **SOLID**, and **ROS 2 best practices**

The system integrates tightly with the official **Stereolabs ZED ROS2 Wrapper**, providing an end-to-end setup from camera drivers to custom acquisition nodes.

---

# **1. Features**

### ✔ ZED 2i Bench Mode

* Real-time ROS2 subscriber to ZED point cloud
* Open3D visualization (filtered, downsampled)
* Validation of sensor data and experiment setup

### ✔ ZED 2i Flight Mode

* Automatic experiment directory creation
* Automated rosbag recording (point cloud + color image + extra topics)
* Reproducible experiment pipeline

### ✔ Modern ROS2 Design

* Nodes implemented using clean OOP structure
* Parameterized via YAML files
* Composable and easily extensible

### ✔ Full Logging & Diagnostics

* Structured logging for all acquisition steps
* Sensor health validation (finite points, bounds, statistics)

---

# **2. System Requirements**

| Component       | Version                               |
| --------------- | ------------------------------------- |
| Ubuntu          | **22.04 LTS**                         |
| ROS 2           | **Humble Hawksbill**                  |
| CUDA            | **11.x or 12.x supported by ZED SDK** |
| ZED SDK         | **v4.x or v5.0.7+**                   |
| Python          | 3.10                                  |
| Open3D          | ≥ 0.17                                |
| C++ build tools | via `build-essential`                 |

---

# **3. Complete Installation Guide**

This section provides a **full clean installation** to ensure the ZED 2i works properly.

---

## **3.1 Install ROS 2 Humble**

Follow the official instructions:

[https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html)

Then:

```bash
sudo apt install python3-colcon-common-extensions \
                 ros-humble-rmw-fastrtps-cpp \
                 ros-humble-rmw-cyclonedds-cpp
```

---

## **3.2 Install CUDA (if needed)**

Check if CUDA is installed:

```bash
nvcc --version
```

If missing, install CUDA recommended by Stereolabs:

[https://docs.nvidia.com/cuda/cuda-installation-guide-linux/](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)

Make sure environment variables exist:

```bash
echo 'export CUDA_HOME=/usr/local/cuda' >> ~/.bashrc
echo 'export CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda' >> ~/.bashrc
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

---

## **3.3 Install Stereolabs ZED SDK**

Download for Ubuntu 22.04:

[https://www.stereolabs.com/developers/release/](https://www.stereolabs.com/developers/release/)

Example installation:

```bash
chmod +x ZED_SDK_Ubuntu22_cuda12.run
./ZED_SDK_Ubuntu22_cuda12.run
```

Verify installation:

```bash
ls /usr/local/zed
```

---

## **3.4 Install ZED ROS2 Wrapper (Mandatory)**

Clone the official wrapper inside the workspace:

```bash
cd ~/Dev/ros2_zed_ws/src
git clone --recursive https://github.com/stereolabs/zed-ros2-wrapper.git
```

Install dependencies:

```bash
sudo apt install ros-humble-image-transport \
                 ros-humble-camera-info-manager \
                 ros-humble-tf-transformations \
                 ros-humble-pcl-conversions \
                 ros-humble-pcl-msgs
```

Build:

```bash
cd ~/Dev/ros2_zed_ws
colcon build --symlink-install
source install/setup.bash
```

Test the camera:

```bash
ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2i
```

If this works correctly, your SDK + CUDA installation is good.

---

## **3.5 Install Open3D (for visualization)**

```bash
pip install open3d
```

---

# **4. Installing This Project**

Clone it into the same workspace where the `zed_ros2_wrapper` is located:

```bash
cd ~/Dev/ros2_zed_ws/src
git clone git@github.com:WeriksonAlves/zed2i_3d_acquisition.git
```

Then build:

```bash
cd ~/Dev/ros2_zed_ws
colcon build --symlink-install
source install/setup.bash
```

---

# **5. Project Structure**

```
zed2i_data_acquisition
├── config
│   ├── topics.yaml
│   ├── zed_bench_config.yaml
│   └── zed_flight_config.yaml
├── docs
│   ├── design_overview.md
│   ├── experiment_protocol.md
│   └── sensor_parameters.md
├── launch
│   ├── zed_bench_visualization.launch
│   ├── zed_flight_record.launch
│   ├── zed_flight_record.launch.py
│   └── zed_full_pipeline.launch
├── LICENSE
├── package.xml
├── README.md
├── resource
│   └── zed2i_data_acquisition
├── setup.cfg
├── setup.py
├── test
│   ├── test_copyright.py
│   ├── test_flake8.py
│   └── test_pep257.py
├── tests
│   ├── test_config.py
│   ├── test_pointcloud_manager.py
│   └── test_rosbag_recorder.py
└── zed2i_data_acquisition
    ├── config.py
    ├── __init__.py
    ├── pointcloud_manager.py
    ├── __pycache__
    │   ├── config.cpython-310.pyc
    │   ├── __init__.cpython-310.pyc
    │   ├── pointcloud_manager.cpython-310.pyc
    │   ├── rosbag_recorder.cpython-310.pyc
    │   ├── visualization.cpython-310.pyc
    │   └── zed_bench_node.cpython-310.pyc
    ├── rosbag_recorder.py
    ├── utils
    │   ├── __init__.py
    │   ├── path_manager.py
    │   └── __pycache__
    │       ├── __init__.cpython-310.pyc
    │       └── path_manager.cpython-310.pyc
    ├── visualization.py
    ├── zed_bench_node.py
    └── zed_flight_node.py
```

---

# **6. Usage**

---

## **6.1 Run ZED Wrapper (must be running for all acquisition)**

```bash
ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2i
```

---

## **6.2 Bench Visualization (Open3D)**

Used to validate camera positioning and depth range.

```bash
ros2 run zed2i_data_acquisition zed_bench_node
```

Expected behavior:

* Waits for first point cloud
* Filters & downsamples points
* Opens Open3D viewer
* Prints statistics to terminal

---

## **6.3 Flight Experiment Recorder**

Records rosbag files for offline processing:

```bash
ros2 run zed2i_data_acquisition zed_flight_node
```

This will:

* Create experiment directory under `/tmp/zed2i_flight_experiments/`
* Start `ros2 bag record`
* Save:

  * Point cloud
  * Left color image
  * Extra topics: TF, IMU

You can later inspect the rosbag with:

```bash
ros2 bag info <bag_folder>
```

---

# **7. Configuration via YAML**

## Flight experiment configuration

`config/zed_flight_config.yaml`

```yaml
zed2i_flight_acquisition:
  ros__parameters:
    experiment_name: "flight_experiment"
    base_output_dir: "/tmp/zed2i_flight_experiments"
    frame_rate: 15
    depth_min: 0.5
    depth_max: 20.0
    altitude_m: 12.0

    point_cloud_topic: "/zed/zed_node/point_cloud/cloud_registered"
    left_image_topic: "/zed/zed_node/left/image_rect_color"

    extra_topics:
      - "/tf"
      - "/zed/zed_node/imu/data"
```

---

# **8. Known Issues / Troubleshooting**

### **ZED SDK reports "CORRUPTED SDK INSTALLATION"**

Cause: TensorRT missing or incorrect CUDA version.
Fix: Reinstall ZED SDK with correct CUDA.

### **Open3D viewer opens but shows nothing**

Cause: invalid or infinite depth points.
Fix: filtering is enabled by default — verify topic exists.

### **Point cloud updates only once**

Expected: Bench mode is meant for static visualization.
Streaming mode will be added in future versions.

---

# **9. License**

MIT License
(Full license text in LICENSE file)

---

# **10. Citation**

If you use this project in academic work:

```
@software{werikson_zed2i_3d_acquisition,
  title={ZED2i 3D Acquisition Framework},
  author={Alves, Werikson},
  year={2025},
  url={https://github.com/WeriksonAlves/zed2i_3d_acquisition}
}
```

---

# **11. Contact**

For questions, suggestions, or collaborations:

**Werikson Frederiko de Oliveira Alves**
Computer Vision & Robotics Research
UFV — NERo Robotics Lab
GitHub: [https://github.com/WeriksonAlves](https://github.com/WeriksonAlves)

