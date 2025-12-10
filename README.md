# **ZED2i Data Acquisition — ROS 2 Humble**

Aquisição, gravação e visualização de dados 3D da câmera **ZED 2i** em ambientes embarcados (ex.: Jetson), com integração nativa a **ROS 2 Humble**, suporte a **rosbag2**, metadados completos de experimento e ferramentas para testes de bancada.

Este módulo faz parte de um projeto maior de comparação multissensorial (ZED 2i, LiDAR, RealSense) com foco em **fusão 3D** e **Geração de mapas OctoMap** para aplicações com drones.

---

## **Visão Geral**

O pacote fornece:

* Classe de alto nível `ZedPointCloudManager` para:

  * Assinatura dos tópicos da ZED 2i
  * Armazenamento do último frame recebido (imagem + nuvem de pontos)
  * Controle completo de gravação via `ros2 bag record`
  * Geração automática de metadados do experimento (`experiment_metadata.json`)
* Nós:

  * `zed_flight_node` — modo voo, gravação completa e robusta
  * `zed_bench_node` — modo bancada, com visualização opcional via Open3D
* Arquivos de configuração YAML para experimentos padronizados
* Arquivos de launch ROS 2
* Arquitetura modular seguindo **SOLID**, PEP8 e boas práticas

---

## **Arquitetura do Pacote**

```
zed2i_data_acquisition/
├── config/
│   ├── zed_flight_config.yaml
│   ├── zed_bench_config.yaml
│   └── topics.yaml
├── launch/
│   ├── zed_flight_record.launch.py
│   ├── zed_bench_visualization.launch
│   └── zed_full_pipeline.launch
├── zed2i_data_acquisition/
│   ├── zed_flight_node.py
│   ├── zed_bench_node.py
│   ├── pointcloud_manager.py
│   ├── rosbag_recorder.py
│   ├── visualization.py
│   └── utils/
│       └── path_manager.py
├── tests/
├── docs/
└── README.md
```

---

## **Instalação**

### **1. Criar workspace ROS 2**

```bash
mkdir -p ~/ros2_zed_ws/src
cd ~/ros2_zed_ws/src
git clone https://github.com/<seu_usuario>/zed2i_data_acquisition.git
cd ..
colcon build
source install/setup.bash
```

### **2. Instalar Open3D (opcional)**

Apenas se desejar visualização 3D no modo bancada:

```bash
pip install open3d
```

---

## **Uso**

### **Modo Voo (Flight Mode)**

Coleta completa 3D durante voo real do drone.

```bash
ros2 launch zed2i_data_acquisition zed_flight_record.launch.py \
    experiment_name:=test_flight_01 \
    base_output_dir:=/data/zed_experiments
```

A estrutura final gerada será:

```
/data/zed_experiments/test_flight_01_YYYYMMDD_HHMMSS/
├── zed2i_recording/
│   ├── metadata.yaml
│   └── zed2i_recording_0.db3
└── experiment_metadata.json
```

Incluindo:

* FOV horizontal/vertical
* Profundidade mínima/máxima
* Distância ideal, altitude
* Lista de tópicos gravados
* Timestamp de criação

---

### **Modo Bancada (Bench Mode)**

Ideal para testar visualização e receber a primeira nuvem de pontos.

```bash
ros2 run zed2i_data_acquisition zed_bench_node
```

Assim que o primeiro `PointCloud2` chegar, uma janela do **Open3D** será aberta.

---

## **Configurações**

### `zed_flight_config.yaml`

Define parâmetros de voo:

```yaml
frame_rate: 15
depth_min: 0.5
depth_max: 20.0
altitude_m: 12.0

point_cloud_topic: "/zed2i/zed_node/point_cloud/cloud_registered"
left_image_topic: "/zed2i/zed_node/left/image_rect_color"

extra_topics:
  - "/tf"
  - "/zed2i/zed_node/imu/data"
```

### `topics.yaml`

Permite padronizar os tópicos da ZED, IMU, transformações, etc.

---

## **Principais Classes**

### **`ZedPointCloudManager`**

Responsável por:

* Gerenciar subscrição dos tópicos
* Armazenar frames mais recentes
* Controlar gravação rosbag2
* Gerar metadados do experimento
* Dar suporte à visualização (bench mode)

### **`RosbagRecorder`**

Abstração do comando:

```
ros2 bag record -o <dir> <topics...>
```

Usa `subprocess.Popen` para máxima portabilidade (Python → C).

### **`ZedConfig`**

Carrega parâmetros diretamente do ROS 2 via `declare_parameter()`.

---

## **Roadmap**

* [x] Estrutura inicial do pacote
* [x] Modo voo — gravação rosbag2
* [x] Metadados automáticos
* [x] Modo bancada — visualização básica
* [ ] Visualização contínua (loop Open3D)
* [ ] Modo multi-sensor (RealSense, LiDAR)
* [ ] Integração com OctoMap
* [ ] Dockerfile (Jetson + ZED SDK + ROS2 Humble)

---

## **Licença**

Este projeto é distribuído sob a licença MIT.
Consulte o arquivo **LICENSE** para detalhes.

---

## **Contato**

Desenvolvido por **Werikson Frederiko**

Doutorando em Ciência da Computação — UFV

Laboratório NERo — Núcleo de Especialização em Robótica

GitHub: [WeriksonAlves](https://github.com/WeriksonAlves)

