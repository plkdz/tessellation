# 自动镶嵌搜索

对应脚本：`src/tiling_explorer.py`

这个脚本从一个基础多边形出发，选择当前有限片的一条裸露边，枚举一块新砖贴上去的候选位置，过滤重叠、断开和边长限制不匹配的候选，然后用显式 DFS 栈继续搜索。

## 核心行为

- 默认预设是 `hat`，也可以用 `--polygon` 传入 JSON 顶点。
- `--allow-reflection` 允许镜像砖。
- `--allowed-length-pairs` 限制可贴合的边长组合。
- `--score-mode bitmap` 用低分辨率位图凹陷度选择下一条裸露边。
- `--score-mode angle` 使用旧的角度采样指标。
- 搜索使用 conflict-directed backjumping，在局部失败时尽量跳回责任块之前。

## 常用命令

```powershell
python src\tiling_explorer.py --preset hat --allow-reflection --allowed-length-pairs "1:1,1:2,2:2,sqrt3:sqrt3" --max-tiles 300 --max-states 20000 --export-every 100 --save-state-h5 --output-dir outputs/dfs_hat
```

## 主要输出

- `trace.csv`：记录 step、块数、栈中待尝试分支、是否导出 PNG、回跳位置和单步耗时。
- `step_<step>_tiles_<count>.png`：按 `--export-every` 导出的当前有限片图像。
- `state_<step>_tiles_<count>.h5`：开启 `--save-state-h5` 后保存的逐步状态。

## 实时查看

搜索器可以通过 `--live-viewer` 同时启动本地查看页。实时查看只影响观察方式，不替代 `trace.csv`、PNG 或 HDF5 输出。
