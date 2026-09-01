# 离线动画和音频

对应脚本：

- `src/render_tiling_animation.py`
- `src/bake_audio.py`

离线动画流程依赖 `src/tiling_explorer.py --save-state-h5` 生成的逐步状态文件。动画脚本读取 HDF5 状态，输出 PNG 帧序列和音频事件缓存；音频脚本再把事件缓存烘焙成 WAV。

## 生成动画帧

```powershell
python src\render_tiling_animation.py --input-dir outputs/dfs_hat --output-dir outputs/dfs_hat_animation --start-step 0 --end-step 19800 --duration 60 --fps 30 --width 1920 --height 1080 --time-gamma 2.0
```

## 生成音频

```powershell
python src\bake_audio.py --events outputs/dfs_hat_animation/audio_events.h5 --output-dir outputs/dfs_hat_animation
```

## 主要参数

- `--fps`：离线动画帧率，默认 `30`。
- `--duration`：动画时长，默认 `60` 秒。
- `--time-gamma`：搜索时间映射曲线，数值越大越偏向前慢后快。
- `--camera-alpha`：虚拟相机平移和缩放的平滑速度。
- `--events-only`：只生成音频事件缓存，不重画帧。

## 输出

- `<animation-dir>/frames`：主画面 PNG 帧。
- `<animation-dir>/removal_crosses`：删除块红叉图层 PNG 帧。
- `<animation-dir>/audio_events.h5`：音频事件缓存。
- `<animation-dir>/add_sound.wav`：添加块音轨。
- `<animation-dir>/remove_sound.wav`：删除块音轨。
