# Maze Out! - Tap Puzzle 关卡解析

对 Grand Games《Maze Out! - Tap Puzzle》（`com.grandgames.arrowjam`，APKPure 909）安装包内置的 **760 关** 做的结构解析：自绘关卡图、每关指标、依赖深度求解和整体统计。

在线文档：https://liuhuan-laofei.github.io/maze-out-level-analysis/

## 说明

- 包内只有 760 关（5 套各自从 1 开始编号的关卡集），线上下发的关卡不在包里，不足 1000 关。
- 1–760 的连续编号是人为拼接（A→B→C→D→E），不是游戏内真实顺序；每关保留原始 `levelId`。
- 图片是按关卡 JSON 自绘的，不是游戏内截图。
- 元素名称由类名和数据结构推断，非官方定义；求解器只建模普通箭头规则，详见站点「方法与说明」。

## 目录

- `docs/`：静态站点（GitHub Pages 从这里发布），含 760 张大图、缩略图、`data/stats.csv`、`data/levels.json`
- `scripts/extract.py`：从 xapk 流式提取关卡 JSON 并拼接为 1–760
- `scripts/render.py` / `render_all.py`：自绘关卡图（需要 Pillow）
- `scripts/stats.py`：结构统计与依赖深度求解

## 复现

```
python3 scripts/extract.py     # 需要把 xapk 放在 ~/Downloads
python3 scripts/stats.py
python3 scripts/render_all.py
```

仅用于游戏关卡设计研究。游戏及关卡数据版权归 Grand Games 所有。
