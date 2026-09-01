# Hat 相关脚本

对应目录：`src/hat/`

这些脚本用于生成已知的 hat 和 `Tile(a,b)` 族有限片镶嵌 SVG。它们不是自动搜索器，而是构造和可视化已知替换结构。

## hat 与镜像 hat

脚本：`src/hat/tile_ab.py`

基于论文中的有限片数据生成 hat 与其镜像块组成的层级镶嵌。当前源数据只支持 `Tile(1,sqrt(3))`，迭代范围是 `0..3`。

```powershell
python src\hat\tile_ab.py -n 3 -o outputs/examples/hat_3.svg
```

## Tile(1,1)

脚本：`src/hat/tile_one_one.py`

生成特殊等边情形 `Tile(1,1)` 的同手性替换镶嵌。

```powershell
python src\hat\tile_one_one.py -n 4 -o outputs/examples/tile_one_one_4.svg
```

## Companion Substitution

脚本：`src/hat/tile_ab_companion_substitution.py`

生成 `Tile(a,b)` 与 `Tile(b,a)` 一起参与的 companion substitution。默认 `a=1`、`b=sqrt(3)`，也就是 hat/turtle 表示。

```powershell
python src\hat\tile_ab_companion_substitution.py -n 4 --a 1 --b 1.7320508075688772 -o outputs/examples/hat_companion_4.svg
```
