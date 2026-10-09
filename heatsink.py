import math
import cadquery as cq

# ===== 可调参数 =====
PLATE_SX = 50.0          # 板 X 尺寸 mm
PLATE_SY = 58.0          # 板 Y 尺寸 mm (气流方向)
TOTAL_H = 10.0           # 总厚度 mm (含鳍片)
PLATE_T = 1.8            # 底板厚度 mm
FIN_H = TOTAL_H - PLATE_T  # 鳍片高度 8.2mm

HOLE_D = 3.0             # 安装孔直径 mm
HOLE_PX = 30.0           # 孔距 X mm
HOLE_PY = 49.0           # 孔距 Y mm (气流方向)
HOLE_CLR = 5.0           # 孔周围净空(孔中心到鳍片, 正方形半边长) mm

FIN_MARGIN = 1.5         # 鳍片区离板边缘距离 mm (1~2)
FIN_PITCH = 3.3          # 鳍片节距 mm (间隙2.3, 深8.2 -> 宽高比1:3.6, 满足深槽规则③ >=1:5)
FIN_T = 1.0              # 鳍片厚度 mm (间隙=2.3mm)
FIN_SEG = 15.0           # 断开分段长度 mm
FIN_BREAK_W = 2.3        # 断开切口宽 mm (同间隙宽, 满足深槽规则)
FIN_XOFF = 1.75          # 鳍片中心网格X偏移 mm (使孔净空边10/20恰好落在间隙中央)

def box(cx, cy, sx, sy, z0, z1):
    return cq.Workplane("XY").box(sx, sy, z1 - z0, centered=(True, True, False)).translate((cx, cy, z0))

def rbox(cx, cy, sx, sy, z0, z1, r):
    return (cq.Workplane("XY")
            .sketch().rect(sx, sy).vertices().fillet(r).finalize()
            .extrude(z1 - z0).translate((cx, cy, z0)))

def cyl(cx, cy, d, z0, z1):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((cx, cy, z0))

# ===== 底板: 直角矩形, z 0 ~ PLATE_T, 中心原点 =====
base = box(0, 0, PLATE_SX, PLATE_SY, 0, PLATE_T)

# ===== 安装孔 x4, 穿透底板 =====
HOLE_XY = [(px, py) for px in (-HOLE_PX / 2, HOLE_PX / 2) for py in (-HOLE_PY / 2, HOLE_PY / 2)]
for hx, hy in HOLE_XY:
    base = base.cut(cyl(hx, hy, HOLE_D, -1, PLATE_T + 1))

# ===== 鳍片: 沿气流方向(Y)长条, 沿X布排, 两端留 FIN_MARGIN =====
x0, x1 = -PLATE_SX / 2 + FIN_MARGIN, PLATE_SX / 2 - FIN_MARGIN
y0, y1 = -PLATE_SY / 2 + FIN_MARGIN, PLATE_SY / 2 - FIN_MARGIN
region = box((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, PLATE_T, PLATE_T + FIN_H)

# 网格按 FIN_XOFF 偏移, 使孔位净空边(x=+-10, +-20)恰好落在鳍片间隙内, 不相切
fins = None
i_lo = math.floor((x0 - FIN_T / 2 - FIN_XOFF) / FIN_PITCH)
i_hi = math.ceil((x1 + FIN_T / 2 - FIN_XOFF) / FIN_PITCH)
for i in range(i_lo, i_hi + 1):
    fx = FIN_XOFF + i * FIN_PITCH
    f = rbox(fx, (y0 + y1) / 2, FIN_T, y1 - y0, PLATE_T, PLATE_T + FIN_H, FIN_T / 2)
    fins = f if fins is None else fins.union(f)
fins = fins.intersect(region)

# ===== 沿气流方向分段断开 =====
L = y1 - y0
ns = max(1, round((L + FIN_BREAK_W) / (FIN_SEG + FIN_BREAK_W)))
seg = (L - (ns - 1) * FIN_BREAK_W) / ns
for k in range(1, ns):
    yb = y0 + k * seg + (k - 0.5) * FIN_BREAK_W
    fins = fins.cut(box((x0 + x1) / 2, yb, x1 - x0 + 2, FIN_BREAK_W, PLATE_T - 1, PLATE_T + FIN_H + 1))

# ===== 孔位净空: 正方形(2*HOLE_CLR), 鳍片避开孔周 =====
for hx, hy in HOLE_XY:
    fins = fins.cut(box(hx, hy, 2 * HOLE_CLR, 2 * HOLE_CLR, PLATE_T - 1, PLATE_T + FIN_H + 1))

base = base.union(fins)

out = 'heatsink'
cq.exporters.export(base, out + '.step')
cq.exporters.export(base, out + '.stl')
print('EXPORTED', out + '.step/.stl')
print('volume mm^3:', round(base.val().Volume(), 1))
