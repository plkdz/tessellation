# 实时查看器

对应脚本：`src/live_viewer.py`

实时查看器是一个小型本地 HTTP 服务。搜索器展开状态时把当前 tiles 序列化成 JSON，通过 SSE 推给浏览器；浏览器用 Canvas 绘制当前状态。

## 使用命令

```powershell
python src\tiling_explorer.py --preset hat --allow-reflection --allowed-length-pairs "1:1,1:2,2:2,sqrt3:sqrt3" --max-tiles 300 --max-states 999999999 --export-every 1000000 --output-dir outputs/dfs_hat_live --live-viewer --live-open --live-every 1
```

## 参数

- `--live-viewer`：启动本地实时查看页。
- `--live-host`：监听地址，默认 `127.0.0.1`。
- `--live-port`：监听端口，默认 `8765`。
- `--live-open`：启动后用默认浏览器打开页面。
- `--live-every`：每展开 N 个 DFS 状态推送一次，默认 `1`。

## 性能边界

浏览器按屏幕刷新率绘制，不会直接阻塞搜索器。搜索器端的主要开销是把当前完整状态转成 JSON；块数很多时可以把 `--live-every` 调大，例如 `10` 或 `50`。

当前实现发送完整状态，不发送增量事件。上万块规模再考虑增量流。
