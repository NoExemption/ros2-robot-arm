# ROS2 Robot Arm Project (Fruit Sorting Edition)

> **致谢与声明 / Acknowledgement**
>
> 本项目基于 **MindSpore Lab** 的开源项目 [ros2_robot_arm](https://github.com/mindspore-lab/orange-pi-mindspore/tree/master/Offline/inference/ros2_robot_arm) 进行复现与改进。
>
> **主要改动点 / Modifications**:
>
> 1.  **识别目标**: 将原有的红绿蓝方块识别，修改为识别带有 **葡萄 🍇、香蕉 🍌、火龙果 🐉** 图片的方块。
> 2.  **硬件适配**: 修改了 URDF 模型以适配特定的机械臂结构，并调整了底层通信协议。
> 3.  **环境部署**: 针对 Orange Pi AI Pro 开发板及 MindSpore Lite 推理引擎进行了适配与测试。

[toc]

## 开发测试

本代码为基于原本 200DK A2 昇腾 om 推理的机械臂代码上，在香橙派 ai pro 上适配了使用 mindspore lite 推理 yolov5s 模型实现机械臂的带有葡萄 🍇、香蕉 🍌 和火龙果 🐉 图片方块分拣功能，目前所测试运行的环境为香橙派 ai pro 20t, 使用的镜像是香橙派官方的 opiaipro_20t_ubuntu22.04_desktop_aarch64_20250211.img.xz, cann 版本为 8.0(镜像自带，不用重新安装)，mindspore 和 mindspore lite 版本为 2.6,需要手动用 pip 命令安装

## 模型说明

本样例代码中使用了 yolov5s 模型，模型文件在本仓库的 ros2_ws\src\dofbot_garbage_yolov5\dofbot_garbage_yolov5\model\目录下，yolov5s_lite_ros.mindir 文件为 mindspore lite 在香橙派的 ai pro 20t 的 310b 环境下的推理文件

##自己训练模型说明
如果准备自己体验模型训练的过程，需要先用机械比的摄像头拍摄 100 张以上 680\*480 分别率的小方块图片，有葡萄、香蕉、火龙果 3 种图片的方块，然后使用昇腾的工具进行标注，工具链接如下：
https://www.hiascend.com/document/detail/zh/Atlas200IDKA2DeveloperKit/23.0.RC2/Getting%20Started%20with%20Application%20Development/iaqd/iaqd_0007.html

标注完成后可以使用 mindyolo 套件进行训练，可以在 mindspore 2.6 310P 环境训练（目前我这边用来训练的环境），训练前需要把标注的格式转成 yolo 格式，mindYolo 套件参考：
https://github.com/mindspore-lab/mindyolo
也可以直接用上述标注的昇腾工具进行训练，不过训练过程是使用 CPU 的，速度会慢一些，昇腾工具训练最终得到的是一个 onnx 文件；

最后参考 mindyolo 的 lite 部署文档进行在 ai pro 上模型导出和转换：
https://github.com/mindspore-lab/mindyolo/tree/master/deploy

注：使用 mindyolo 训练模型后得到的是 ckpt 文件，然后根据上述文档导出为 mindir 格式，然后再用 lite 工具转成 lite 专用的 mindir 文件（后缀还是 mindir，但转换后可以加快启动速度）；如果是用的昇腾工具训练的，就直接用 lite 工具把 onnx 文件转成 lite 专用的 mindir 文件；

获取到 lite 专用 mindir 文件后，放置到 ros2_ws\src\dofbot_garbage_yolov5\dofbot_garbage_yolov5\model\目录下即可，即上述的 yolov5s_lite_ros.mindir 文件

## aipro 环境准备

准备环境中，下载代码和安装依赖都需要联网，香橙派 ai pro 支持网线连接路由器，或者 usb 连接电脑联网，或者 wifi 联网；

关于机械臂组装的操作，可以参考以下昇腾文档：
https://www.hiascend.com/document/detail/zh/Atlas200IDKA2DeveloperKit/23.0.RC2/Application%20Cases/raadg/raadg_0002.html
该文档中使用的开发板是 200DK A2,但机械臂的组装方法是一样的

### 下载代码

默认用 root 账户运行，香橙派的镜像中 cann 环境默认都配置在 root 账户下，如果切换其他账户，可能需要重新设置环境变量；
将本仓库的代码目录下载到/root 目录下面，如果是其它目录的话，会出现 urdf 文件读取不到的问题，原因是 ROS 的 CPP 代码中把路径写死在了里面，如果需要用其它目录，可以参考以下链接进行修改：
https://developer.huawei.com/home/forum/ascend/thread-0297149164470390076-1-1.html

### 预备步骤

确保 ai pro 联网。

在`~/.bashrc`文件末尾新增一行：`conda deactivate`（**注：不用机械臂时，请自行将这一行注释掉**），随后保存并退出`~/.bashrc`文件，在命令行中输入`source ~/.bashrc`

使用链接（[https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/Atlas%20200I%20DK%20A2/DevKit/samples/23.0.RC1/e2e-samples/Arm/robot_arm_dependency.zip]）下载依赖压缩文件，将该压缩文件放入`ros2_robot_arm`文件夹中。使用`unzip robot_arm_dependency.zip`命令对依赖文件压缩包进行解压。

### 安装 ROS

请按照顺序依次执行如下命令：

1. `sudo apt install -y software-properties-common`
2. `sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg`（**本条命令将尝试访问 github，如遇卡顿，请多尝试几次**）
3. `echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null`
4. `sudo apt update`
5. `sudo apt install -y libegl-mesa0`
6. `sudo apt install -y ros-humble-desktop`
7. `sudo apt install -y python3-colcon-common-extensions`
8. `sudo apt install -y pip`

### 安装 mindspore 2.6 和 mindspore lite 2.6 云测 python 包

请按照顺序依次执行如下命令：

1. `pip3 install https://ms-release.obs.cn-north-4.myhuaweicloud.com/2.6.0/MindSpore/unified/aarch64/mindspore-2.6.0-cp310-cp310-linux_aarch64.whl --trusted-host ms-release.obs.cn-north-4.myhuaweicloud.com -i https://pypi.tuna.tsinghua.edu.cn/simple`
2. `pip3 install https://ms-release.obs.cn-north-4.myhuaweicloud.com/2.6.0/MindSpore/lite/release/linux/aarch64/cloud_fusion/python310/mindspore_lite-2.6.0-cp310-cp310-linux_aarch64.whl -i https://pypi.tuna.tsinghua.edu.cn/simple`
3. `pip3 install mindyolo -i https://pypi.tuna.tsinghua.edu.cn/simple`

### 安装其他依赖

进入目录`ros2_robot_arm`，执行如下命令

1. `pip3 install -r requirements.txt`
2. `sudo dpkg -i libconsole-bridge0.4_0.4.4+dfsg-1build1_arm64.deb`
3. `sudo dpkg -i liburdfdom-world_1.0.0-2ubuntu0.1_arm64.deb`

将如下环境变量添加至`~/.bashrc`文件中  
`LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib:/usr/lib/aarch64-linux-gpu:/usr/local/lib`  
随后执行：`source ~/.bashrc`

将`libdofbot_kinemarics.so`放入`/usr/lib`中：`cp libdofbot_kinemarics.so /usr/lib`

### 安装 orocos_kdl

进入目录`ros2_robot_arm`，依次执行如下命令

1. `cd orocos_kdl && mkdir build && cd build`
2. `cmake ..`
3. `make -j4`
4. `sudo make install`

### 安装机械臂底层驱动

进入目录`ros2_robot_arm`，执行如下命令

1. `cd 0.py_install`
2. `python3 setup.py install`

### 编译工作空间

进入目录`ros2_robot_arm`，

1. `. setenv.sh`，执行完出现提示信息：`-bash: ./ros2_ws/install/setup.bash: No such file or directory`，忽略即可。
2. `sequenceDiagram
   participant 相机
   participant 主控
   participant ROS节点
   participant 推理
   participant 后处理
   participant 缓冲
   participant 映射
   participant 反解服务
   participant 运动控制
   participant 机械臂

相机->>主控: 采集图像
主控->>ROS节点: 发布图像
ROS节点->>推理: YOLOv5s 轻量推理
推理->>后处理: 阈值过滤与NMS
后处理->>缓冲: 多帧一致性判断
缓冲-->>主控: 稳定目标
主控->>映射: 像素→机械臂XY
映射->>反解服务: 请求关节角
反解服务-->>主控: 返回关节角
主控->>运动控制: 轨迹规划（靠近/夹取/抬起/放置/复位）
运动控制->>机械臂: 执行动作`3.`source ./install/setup.bash`

## 硬件连接

以 ai pro 为中心，用网线与计算机相连，用 40pin 排线与机械臂相连（注意排线的两头都是母头），用 USB 线与装在机械臂的摄像头相连，并连接电源通电；

硬件示意图：

![](./imgs/2.png)

## 校准摄像头（**该步骤仅供初次使用！后续可跳过此步骤**）

目的：可视化界面调整摄像头位置，确保整个十字框可见

为确保方框无法被摄像头拍摄全的问题，现补充图形化界面。

在原终端的/root/下运行 jupyter notebook：`jupyter notebook --allow-root`（如在**MobaXTerm**中启动，则需要添加 DK 的 ip，并在/root 目录下运行。实例命令：`jupyter notebook --allow-root --ip 192.168.137.100`）。若生成的其中一个 url 访问不成功，可以尝试另外一个

**----------注意 1：----------**

第一次启动时可能会有输入密码的情况

![](./imgs/9.PNG)

这个时候，密码在终端中：

![](./imgs/10.jpg)

将红框部分复制粘贴即可。

**------注意部分结束----------**

在 Jupyter notebook 中逐级点击进入目录：`/root/ros2_robot_arm/ros2_ws/src/dofbot_garbage_yolov5/tools`，最终进入`相机校准.ipynb`

![](./imgs/18.PNG)

随后在如下图所示的`Kernel`选择栏中，点击`Restart & Run All`

![](./imgs/11.PNG)

**----------注意 2：----------**

首次启动后，拉到最下方可能不会有任何显示。如下图所示：

![](./imgs/14.PNG)

此时拉会到最上方并点击`Restart & Run All`即可。多跑几次，直到出现图形界面为止。

**------注意部分结束----------**

出现的图形界面如下：

![](./imgs/12.PNG)

图形界面使用步骤如下：

1. 点击`calibration_model`，点击后，拉动上方的滚动条（`joint1`和`joint2`），随着滚动条的拉动，蓝色边框会出现，**请务必确保蓝色边框覆盖整个十字框，具体效果如下（请确保测试环境具备充足的灯光！）：**

![](./imgs/13.PNG)

2. 当效果如上图所示时，点击`calibration_ok`按钮，则可视化界面进入方框内部。具体效果如下图所示：

![](./imgs/16.PNG)

**----------注意 3：----------**

在调整完显示框后，应关闭 jupyter notebook 的程序，避免与 python 主程序发生摄像头冲突。建议使用`Restart`命令进行关闭，如下图所示：

![](imgs/22.PNG)

**------注意部分结束----------**

回到终端，使用`Ctrl C`命令终止`jupyter notebook`程序

## 启动机械臂单个小方块抓取

开启两个窗口，每个窗口下都执行如下操作，
进入目录`ros2_robot_arm`，
在每个窗口下都执行`.s etenv.sh`
在第一个窗口中执行：`ros2 run dofbot_moveit dofbot_server`
在第二个窗口中执行：`ros2 run dofbot_garbage_yolov5 block_cls`

## 对于抓取不准的问题，需针对首次抓取结果，人工修正硬件噪声（**该步骤仅供初次使用！后续可跳过此步骤**）：

经过对比不同机械臂发现，即使是相同商家生产的机械臂，每一款产品在出厂时也存在硬件上的规格差异，俗称噪音，**如果首次存在无法抓取的情况，玩家需要根据自己手中的机械臂手动配置噪声参数**

通过如下命令进入配置文件的目录：

```
cd /root/ros2_robot_arm/ros2_ws/src/dofbot_garbage_yolov5/dofbot_garbage_yolov5/config
```

使用通过`MobaXTerm`或`vim`工具修改`offset.txt`文件，在该 txt 文件中修改噪音参数：

1. 如发现机械臂抓取略微靠后（色块后方），导致无法抓取，则需要适当加大该参数（如从 0.008 修正到 0.01）
2. 如发现机械臂抓取略靠前（色块前方），导致无法抓取，则需要适当减少该参数（如从 0.008 修正到 0.006）

反复修改该参数，重复该流程，直到合适抓取位置。

随后，将该配置目录下的配置文件`XYT_config.txt`、`dp.bin`、`offset.txt`复制粘贴到如下目录：`/root/ros2_robot_arm/ros2_ws/src/robot_arm_color_stacking/robot_arm_color_stacking/config`中。使得下一步骤的堆叠功能，共享当前的配置
