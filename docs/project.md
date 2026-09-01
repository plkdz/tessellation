# 项目总览

本项目用于整理和实验平面镶嵌问题，重点关注单一形状能否密铺平面、能否强迫非周期，以及如何用程序搜索和渲染有限片镶嵌。

## 主要内容

- `src/hat/`：生成 hat、`Tile(1,1)` 和 companion substitution 的有限片 SVG。
- `src/tiling_explorer.py`：从单块多边形出发做边界生长搜索。
- `src/live_viewer.py`：给搜索器提供本地实时 Canvas 查看页。
- `src/render_tiling_animation.py`：把搜索保存的 HDF5 状态渲染成 PNG 帧序列。
- `src/bake_audio.py`：把动画事件缓存烘焙成 WAV 音轨。

## 当前推荐流程

1. 用 `src/hat/*.py` 生成已知替换镶嵌示例。
2. 用 `src/tiling_explorer.py` 探索有限片拼法。
3. 搜索时需要观察过程，就加 `--live-viewer`。
4. 需要离线成片，就用 `--save-state-h5` 保存状态，再运行动画和音频脚本。

## 输出目录

正式搜索输出默认放在 `outputs/dfs_hat` 或调用命令指定的目录下。`outputs/` 被 Git 忽略，临时验证结果不要提交。
