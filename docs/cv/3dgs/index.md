# 3D Gaussian Splatting

**三维高斯泼溅**是一种 3D 重建技术。在当前AI盛行的时代，它没有使用复杂的神经网络，而是直接面向场景优化，使用几何直观的 3D Gaussians 来做训练，反向传播所求的偏导数也均有物理意义。它的效果也在多种场景下胜过使用 MLP 的 NeRF ，并且计算开销更小。

笔记的“理论”部分是对整个 3DGS pipeline 的讲解，按照论文逻辑梳理；“实践”部分简单记录了我自己的训练情况；“附录”部分有部分数学公式的推导，是对“理论”部分的补充。

我对于 3DGS 的理解尚浅，笔记中难免有疏漏之处，还望指出。

<br><br><br>

# 评论区

<script src="https://giscus.app/client.js"
        data-repo="St-AnonTokyo/notebook"
        data-repo-id="R_kgDOTN4hJw"
        data-category="Announcements"
        data-category-id="DIC_kwDOTN4hJ84DAqUo"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="1"
        data-input-position="top"
        data-theme="preferred_color_scheme"
        data-lang="zh-CN"
        data-loading="lazy"
        crossorigin="anonymous"
        async>
</script>