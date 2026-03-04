MindYolo 机械臂项目配置与运行指南

一、URDF 文件修改与验证

1. 覆盖 URDF 内容：将自定义机械臂 URDF 内容覆盖至 ros2_ws/src/dofbot_moveit/urdf/dofbot.urdf
2. 关键修改：

1) 修改文件中 armpi_fpv 路径
2) 删除 base_link 对应的 <inertial> 块（消除 KDL 根链接惯性警告）

3. 验证修改结果：
   ros2 launch dofbot_moveit dofbot_moveit.launch.py gui:=true

二、通信协议适配与驱动安装

1. 协议修改：基于原有 arm_protocol.py 封装，修改为适配项目的 Arm_Lib.py（替换原 40Pin 连接通信协议）
2. 适配调整：调试并修改通信协议中 0~1000 与 0~240° 的映射关系，确保适配项目需求
3. 安装底层驱动（覆盖旧版本）：
   cd /root/ros2_robot_arm/0.py_install
   python3 setup.py install

三、系统环境配置

1. 关闭 conda 环境（若已激活）：
   conda deactivate
2. 修改 .bashrc 文件，添加以下环境变量配置：

# 加载昇腾（Ascend）工具包环境

source /usr/local/Ascend/ascend-toolkit/set_env.sh

# 加载 ROS 2 Humble 环境

source /opt/ros/humble/setup.bash

# 加载 ros2_robot_arm 工作空间

source /root/ros2_robot_arm/ros2_ws/install/setup.bash

# 配置库文件路径

LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib:/usr/lib/aarch64-linux-gpu:/usr/local/lib

四、程序测试与调试

1. 启动机械臂服务：
   ros2 run dofbot_moveit dofbot_server
2. 运行目标检测节点：
   ros2 run dofbot_garbage_yolov5 block_cls
3. 启动可视化界面（查看检测结果）：
   ros2 run rqt_image_view rqt_image_view
4. 调试优化：根据运行结果修改程序初始姿态等参数，确保流程跑通并逐步完善

五、模型训练与格式转换

1. 数据集与训练

1) 准备数据集：收集包含三种带水果图片的方块数据
2) 完成数据标注，训练 YOLOv5 模型，得到 best.pt 权重文件

2. 模型格式转换（PT → ONNX → MINDIR）

1) PT 转 ONNX：
   python export.py --weights runs/train/yolov5s_custom/weights/best.pt --include onnx --img 640 --simplify
2) ONNX 转 lite专用MINDIR（使用 MindSpore Lite 2.6.0 转换器）：
   cd /root/mindspore-lite-2.6.0-linux-aarch64/tools/converter/converter
   ./converter_lite \
    --fmk=ONNX \
    --modelFile=/root/yolov5/runs/train/exp/weights/best.onnx \
    --outputFile=/root/yolov5/runs/train/exp/weights/yolov5s_lite_ros \
    --device=Ascend \
    --inputShape="images:1,3,640,640" \
    --inputDataFormat=NCHW \
    --optimize=ascend_oriented \
    --configFile=/root/ros2_robot_arm/ascend.cfg \
    --outputDataType=FLOAT \
    --saveType=MINDIR

3. 替换模型：将生成的 .mindir 文件替换项目中原有的模型文件
