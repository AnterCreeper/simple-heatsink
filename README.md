# simple-heatsink

可参数化的铲齿/铣槽式铝散热片生成器，基于 [CadQuery](https://cadquery.readthedocs.io/)，一键导出 STEP / STL。

当前默认参数适配 **QL45452** 散热（50×58×10mm，孔距 30×49mm ⌀3）。

## 特性

- 底板 + 沿气流方向的直鳍片，鳍片沿流向分段断开（利于铣削与气流扰动）
- 4 个安装孔，孔周正方形净空自动避让鳍片
- 鳍片网格可偏移（`FIN_XOFF`），使净空边缘恰好落在鳍片间隙内，不产生半根残鳍
- 默认几何满足常见 CNC 深槽检测规则（槽深 8.2mm / 宽 2.3mm，宽高比优于 1:5）

## 使用

```bash
pip install cadquery
python heatsink.py   # 生成 heatsink.step / heatsink.stl
```

## 参数

全部参数在 `heatsink.py` 顶部，单位 mm：

| 参数 | 默认 | 说明 |
|---|---|---|
| `PLATE_SX` / `PLATE_SY` | 50 / 58 | 板尺寸，SY 为气流方向 |
| `TOTAL_H` | 10 | 总厚度（含鳍片） |
| `PLATE_T` | 1.8 | 底板厚度，鳍片高 = `TOTAL_H - PLATE_T` |
| `HOLE_D` / `HOLE_PX` / `HOLE_PY` | 3 / 30 / 49 | 安装孔直径与孔距（PY 沿气流方向） |
| `HOLE_CLR` | 5.0 | 孔位正方形净空半边长 |
| `FIN_MARGIN` | 1.5 | 鳍片区距板边缘距离 |
| `FIN_PITCH` / `FIN_T` | 3.3 / 1.0 | 鳍片节距 / 厚度（间隙 = 节距 - 厚度） |
| `FIN_SEG` / `FIN_BREAK_W` | 15 / 2.3 | 分段长度 / 断开切口宽 |
| `FIN_XOFF` | 1.75 | 鳍片网格 X 偏移，用于对齐孔净空边界 |

修改节距或孔距后，建议校验净空边（`HOLE_PX/2 ± HOLE_CLR`）是否仍落在鳍片间隙内，必要时调整 `FIN_XOFF`。

## License

MIT
