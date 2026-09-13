# 3D Gaussian Splatting 入门

有用资源指路：

👉原论文：[https://arxiv.org/pdf/2308.04079](https://arxiv.org/pdf/2308.04079)

👉论文仓库：[https://github.com/graphdeco-inria/gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting)

👉OpenCV的讲解网站：[https://learnopencv.com/3d-gaussian-splatting](https://learnopencv.com/3d-gaussian-splatting)

本文主要基于上述资料完成，粗浅地介绍了3dgs的理论基础。

---

## Introduction

!!! question "3D reconstruction from multiple images"

    根据一组从不同角度和位置拍摄的二维照片构建一种三维表示。我们希望后续能够通过这个3d模型复现整个场景。

对于这个问题，我们要考虑主要有三点：

- 如何表示这个场景
- 如何根据已有的二维信息来建构这个表示模型
- 如何使用这个模型

## Related Work

下面简单介绍一些常用的3d重建方法，虽然本文要介绍的3dgs解决问题的性能普遍更优，但它以这些技术为基础，相关性较强，所以有必要了解一下。

### Photogrammetry

这是最早用来解决这个问题的方法。

???+ note "基本原理"
    *"All these methods re-project and blend the input images into the novel view camera, and use the
    geometry to guide this re-projection."*

    ![流程图](img/photogrametry.webp "SFM流程图")

    - **Input：**[Intrinsic Matrix](https://blog.csdn.net/gwplovekimi/article/details/90172544 "清楚简明的介绍")（3×3的内参矩阵K）用来描述单个相机拍摄图片的过程，即现实世界的点如何投影到2D平面上（三维点坐标到二维点坐标的映射关系），Image Frames是一组从不同位置、角度拍摄采集的照片样本。  
    - **Feature Extraction：**系统在每张图片中找容易被重复识别的特征点（如边角处、边缘处、纹理较明显的位置等），即图中绿色点。(feature points)
    - **Feature Matching：**系统在不同图片的特征点之间寻找对应关系，也就是那些从不同视角都能看到的点，对应现实中同一个3D点。
    - **Camera Pose Estimation：**有了这两个方面的点的信息，我们就可以估计照下每张图片的相机之间的相对位置和朝向。我们用3×4的外参矩阵[R|t]表示相机的这两个信息（左边三列是旋转矩阵，右边一列是平移向量——这里采用了齐次坐标，这样坐标经过矩阵乘法后就自动把平移量加上了）。其中旋转矩阵R描述了相机的朝向，平移向量t描述了相机的平移，两者一起把世界坐标系中的3D点变换到相机坐标系，相机的朝向和位置构成相机的“位姿”(Pose)。

    &emsp;&ensp;   👉内参矩阵描述的是相机自身的成像方式，外参矩阵描述的是相机在世界坐标系中的信息。3D点先经过外参矩阵从世界坐标系变换到相机坐标系，而后经过内参矩阵投影到二维平面上。我们希望从这些2D点恢复原来的3D点。

    - **3D Mapping：**知道了多个相机的位置后，有了同一个点在多个角度的信息，我们就可以通过三角化(triangulation)计算/恢复空间中某个点的3D坐标，得到图中的点云。简单来说就是把不同位置得到的2D投影点反投影成一条3D射线，这些射线的相交处，就是我们要找的3D点。
    - **Bundle Adjustment：**这是优化步骤，它会同时优化相机矩阵和3D点的位置，目标是让3D点重新投影到2D后，尽可能接近原图中检测到的2D特征点。
    - **Loop Closure：**将相机围绕某个场景拍照，理论上相机轨迹应该闭合。然而，移动过程中，相机的位姿难免会存在误差（例如：相机不会完美按照预期轨迹和理想角度、有噪音干扰等），这些小误差逐步累积，可能导致系统误判起点和终点的距离，导致轨迹无法闭合。这个步骤通过特征匹配来识别高度相似的图像，找到分离的起终点，判断实际回环的位置。
    - **Pose Graph Optimization：**检测到回环后，系统会全局调整所有相机的位置和朝向，优化相机矩阵，使整体线路闭合。

**阶段**

- Structure from Motion (SfM)：估计相机位姿，恢复稀疏点云。
- Multi View Stereo (MVS)：在相机位姿的基础上估计像素深度，生成稠密点云。
- Dense reconstruction：进一步生成更完整的三维模型

👉上面的流程图展示的是SFM的原理，后续还要经过MVS和Dense reconstruction来得到更完整的3D模型

**性能**

*"These methods produced excellent results in many cases, but typically cannot completely recover from unreconstructed regions, or from “over-reconstruction”,
when MVS generates inexistent geometry."*

### Neural Rendering and Radiance Fields（NeRF）

NERF为3d重建引入了深度学习方法。

???+ note "NeRF步骤"

    ![Vanilla NeRF Pipeline](img/nerf.webp)
    
    - 建立辐射场函数 $F_\Theta(\mathbf{x}, \mathbf{d}) \rightarrow (\sigma, \mathbf{c})$

        输入： 
        
        1. 位置： $\mathbf{x}=(x,y,z)$
        2. 观察方向：$\mathbf{d}=(\theta,\phi)$

        输出： 体密度 $\mathbf{\sigma}$和RGB颜色 $\mathbf{c}$

        👉建模时假设物体各向同性，因此体密度仅由位置决定，与看的视角无关。颜色由位置、方向共同决定（镜面反射、材质折射率······）

    - 采样光线：对训练图上每个像素，从**相机中心**向其发一条射线，沿射线离散采样一组点作为样本。（巨量的样本！）
    - [位置编码](https://blog.csdn.net/leviopku/article/details/133317676)（positional encoding）：利用一组 $\sin/\cos$ 把坐标映射成一组正弦基 $\gamma(p) = \big(\sin(2^0\pi p), \cos(2^0\pi p),\ \sin(2^1\pi p), \cos(2^1\pi p),\ \dots,\ \sin(2^{L-1}\pi p), \cos(2^{L-1}\pi 
    p)\big)$

    &emsp; 把原先的输入提升成更高维的向量（维数$\times 2 L$倍）。
    
    &emsp; 🤔MLP（多层感知机）用梯度下降训练时，对输入的“分辨率”不够，难以识别微小的差异和变动。因此它天然倾向于学会较低频（在空间中变化慢）的函数，难以学会高频（在空间中变化快）的函数。

    ??? example "位置编码的例子"

        假设坐标归一化到 $[-1,1]$，考虑两个相邻点$x = 0.500$ 和 $x = 0.501$：

        - 直接输入网络：输入只差0.001，经过几层ReLU后，输出差异微乎其微。
        - 经过位置编码：令$L=10$，在$k=9$那一维是 $\sin(512\pi \Delta x)$，两个点的相位差被放大到 $512\pi \times 0.001 \approx 1.6$ 弧度，约为四分之一周期。

        位置编码使两点的差异沿不同频率被放大了 $2^k \pi$ 倍，让神经网络能够识别出微小变动。

        💡一个有趣的事实：为了避免周期性对样本的影响（两个坐标点映射到的高维向量完全一致），这种编码方式有两重防御机制。

        - sin/cos成对： $(\sin\theta, \cos\theta)$ 唯一确定一组极坐标，让函数在同周期内保持单射。
        - 要整体编码碰撞，必须在所有 $k=0,\dots,L-1$ 上同时对齐：

            令 $d=\Delta p$，则
            
            $$2^{k}\pi d \equiv 0 \pmod{2\pi} \iff 2^{k-1}d \in \mathbb{Z}, \quad \forall k$$

            考察k的不同取值：$k=0$ 给出 $d \in 2\mathbb{Z}$，$k=L-1$ 给出 $d \in 2^{2-L}\mathbb{Z}$，交集仍是 $d \in 2\mathbb{Z}$。

            因此，当且仅当d是偶数，编码才会在所有频率方向都无差异。而NeRF的坐标归一化到 $p \in [-1,1]$，宽度正好等于2，所以唯一会碰撞的只有 $\gamma(-1) = \gamma(1)$。这是边界，对域内的识别无影响。

    - 进入MLP：位置编码后的 $\mathbf{x}$ 先进网络 → 输出 $\sigma$ 和一个中间特征；中间特征再拼上编码后的 $\mathbf{d}$ → 最后输出颜色 $\mathbf{c}$。

    - [体渲染](https://blog.csdn.net/qq_42415112/article/details/134351239)（Volume Rendering）： 把这些离散点的颜色按不透明度从前往后加权累加，处理物体的遮挡与前后关系。

    $$\hat{C}(\mathbf{r}) = \sum_{i} T_i (1-e^{-\sigma_i\delta_i}) \mathbf{c}i  \quad T_i = e^{-\sum{j<i}\sigma_j\delta_j}$$

    - 损失 + 优化：把渲染出的像素颜色 $\hat{C}$ 和真实照片颜色对比，使用反向传播调参。

###  Point-Based Rendering and Radiance Fields

**点渲染（Point-Based Rendering）**

体渲染的离散形式，用点云来表示场景，把点投影到屏幕上来画图。点云通常来自Photogrammetry的 SfM 或 MVS 。

$\hat{C} = \sum_{i=1}^N T_i (1-e^{-\sigma_i\delta_i}) c_i, \qquad T_i = \prod_{j=1}^{i-1} e^{-\sigma_j \delta_j}$

*While true to the underlying data, point sample rendering suffers from holes, causes aliasing, and is strictly discontinuous.*

🤔我们可以通过“ **Splatting** ”来解决这些问题——给每个点添加影响范围与权重，让它在屏幕上平滑地摊开。

👉3D高斯就是一种 Splatting 的方法。

**辐射场（Radiance Field）**

- 隐式辐射场：把5D坐标映射到密度&颜色，在NeRF中使用。它是续可微的，但是神经网络的开销很大。
- 显式辐射场：直接使用点云作为辐射场的骨架，每个点携带可学习的特征，在渲染时解码。它几何直观，训练快速，但只能 handle 简单的场景。

下面要谈的3DGS巧妙地把两种方向的优点缝合了起来。

*We first introduce 3D Gaussians as a flexible and expressive scene representation.
We start with the same input as previous NeRF-like methods, i.e.,
cameras calibrated with Structure-from-Motion (SfM) [Snavely et al.
2006] and initialize the set of 3D Gaussians with the sparse point
cloud produced for free as part of the SfM process.*

## Overview

