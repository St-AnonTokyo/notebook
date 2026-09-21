# 附录：The Math in 3D Gaussians



---

## 3D Gaussian 代数推导

从一维出发逐步推广到 d 维的**高斯分布**表达式。

### 一维

**一维正态分布公式**

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}}\exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)$$

我们将指数部分改写，让结构更清晰

$$-\frac{(x-\mu)^2}{2\sigma^2} = -\frac{1}{2}(x-\mu)(\sigma^2)^{-1}(x-\mu)$$

### 逐项推广

| 一维 | d 维 | 解释 |
| :--: | :---: | :--: |
|  $x$ | $\mathbf{x}$ | 标量 → 向量 |
| $\mu$ | $\boldsymbol{\mu}$ |标量 → 向量 |
| $\sigma^2$ | $\Sigma$ |方差 → [协方差矩阵](https://en.wikipedia.org/wiki/Covariance_matrix)|
|$(\sigma^2)^{-1}$|$\Sigma^{-1}$|标量倒数 → 矩阵求逆|
|相乘|$(\cdot)^{\top}\Sigma^{-1}(\cdot)$|标量乘法 → [二次型](https://en.wikipedia.org/wiki/Quadratic_form)|
|$\frac{1}{\sigma\sqrt{2\pi}}$|$\frac{1}{(2\pi)^{d/2} \vert \Sigma \rvert ^{1/2}}$|归一化处理，保证$\int \cdot = 1$|

???+ question "归一化的系数从何而来？"

    为使总体积分为 1 ，先积指数项。这里可以直接使用[高斯积分](https://zh.wikipedia.org/wiki/%E9%AB%98%E6%96%AF%E7%A7%AF%E5%88%86)的结论：

    $$\int_{\mathbb{R}^d}\exp\Big(-\tfrac{1}{2}\mathbf{x}^{\top}\Sigma^{-1}\mathbf{x}\Big)d\mathbf{x} = (2\pi)^{d/2}|\Sigma|^{1/2}$$

    系数取倒数即可。

最终，我们得到**高维正态分布（高斯分布）公式**：

$$f(\mathbf{x}) = \frac{1}{(2\pi)^{d/2}|\Sigma|^{1/2}}\exp\Big(-\tfrac{1}{2}(\mathbf{x}-\boldsymbol{\mu})^{\top}\Sigma^{-1}(\mathbf{x}- \boldsymbol{\mu})\Big)$$

$\mathbf{x}$ 服从高斯分布，记为：

$$\mathbf{X}\sim\mathcal{N}(\boldsymbol{\mu},\Sigma)$$



???+ note "3D Gaussian 表达式"

    3D Gaussian ≈ 三维高斯分布，但没有归一化系数。因为 3DGS 是为了在从中心向外的一定范围内，给空间点赋予权重，中心取1、向外衰减，而不是为了算概率密度。于是，我们得到 3DGS 的表达式：

    $$G(\mathbf{x}) = \exp\Big(-\tfrac{1}{2}(\mathbf{x}-\boldsymbol{\mu})^{\top}\Sigma^{-1}(\mathbf{x}-\boldsymbol{\mu})\Big)$$

👉实际上，指数就是所谓[马氏距离](https://zhuanlan.zhihu.com/p/46626607)的平方 $\Delta^2 = (\mathbf{x}-\boldsymbol{\mu})^{\top}\Sigma^{-1}(\mathbf{x}-\boldsymbol{\mu})$ ，用来给空间分配恰当的权重。它修正了欧氏距离各个维度尺度不一致的问题。

## 3D Gaussian 几何形状

高维高斯分布一般描述的是椭球面，这是由公式性质造成的,我们可以把它转变成我们更熟悉的椭球形式。

考察水平集 ${\mathbf{x} : (\mathbf{x}-\boldsymbol{\mu})^{\top}\Sigma^{-1}(\mathbf{x}-\boldsymbol{\mu}) = c}$

### 特征分解

由于$\Sigma$ 对称且正定，因此可以将其[特征分解](https://zh.wikipedia.org/wiki/%E7%89%B9%E5%BE%81%E5%88%86%E8%A7%A3)：

$$\Sigma = Q\Lambda Q^{\top}, \qquad 其中 \quad Q^{\top}Q = I,\quad \Lambda = \mathrm{diag}(\lambda_1,\dots,\lambda_d),\ \lambda_i > 0$$

于是

$$\Sigma^{-1} = Q\Lambda^{-1}Q^{\top} = \sum_i \frac{1}{\lambda_i}\mathbf{u}_i\mathbf{u}_i^{\top}$$

### 坐标变换

令 $\mathbf{y} = Q^{\top}(\mathbf{x}-\boldsymbol{\mu})$（旋转），则

$$\Delta^2 = (\mathbf{x}-\boldsymbol{\mu})^{\top}Q\Lambda^{-1}Q^{\top}(\mathbf{x}-\boldsymbol{\mu}) = \mathbf{y}^{\top}\Lambda^{-1}\mathbf{y} = \sum_i \frac{y_i^2}{\lambda_i}$$

### 方程形式

等值面变成 $\sum_i \dfrac{y_i^2}{\lambda_i} = c$，两边同除以 $c$：

$$\boxed{\ \sum_i \left(\frac{y_i}{\sqrt{c,\lambda_i}}\right)^2 = 1\ }$$

这是 $\mathbf{y}$ 坐标系内的标准椭球方程，半轴长度是 $\sqrt{c\lambda_i}$。

因为 $\mathbf{y}$ 坐标是由 $\mathbf{x}$ 坐标旋转得到的，因此在原坐标系中，这是一个被旋转过的椭球。

### 对应关系

|几何量|代数量|
|:---:|:---:|
|椭球中心|$\boldsymbol{\mu}$|
|半轴方向|$Q$ 的列 / $\Sigma$ 的特征向量|
|半轴长度|$\sqrt{c\lambda_i}$ = $\sqrt{c}\cdot\sqrt{\textbf{特征值}}$|

