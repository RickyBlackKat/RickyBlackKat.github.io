#!/usr/bin/env python3
"""Compose KAT-5 blueprint sheets (SVG) from OpenSCAD projections."""
import re, json, base64, math, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, 'proj')
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)

W, H = 1700, 1100                      # 17 x 11 in sheet, 100 units / inch
BG, PAPER = '#0d3a72', '#0d3a72'
INK, THIN, FAINT, GRID, ACC = '#eef5ff', '#b9d3f5', '#7fa6dc', '#174684', '#ffd27a'
FONT = "'DejaVu Sans Condensed','DejaVu Sans','Liberation Sans',sans-serif"
MONO = "'DejaVu Sans Mono','Liberation Mono',monospace"
DATE = '2026-11-26'
N_SHEETS = 7

# ---------------------------------------------------------------- geometry
def load(name):
    """Polygons (model mm) from an OpenSCAD 2D SVG export (y is written negated)."""
    s = open(os.path.join(PROJ, name + '.svg')).read()
    polys = []
    for d in re.findall(r'd="([^"]+)"', s):
        for sub in re.split(r'[Mm]', d):
            pts = re.findall(r'(-?[\d.]+(?:e-?\d+)?),(-?[\d.]+(?:e-?\d+)?)', sub)
            if len(pts) > 1:
                polys.append([(float(x), -float(y)) for x, y in pts])
    return polys

def bbox(polys):
    xs = [p[0] for pl in polys for p in pl]; ys = [p[1] for pl in polys for p in pl]
    return min(xs), min(ys), max(xs), max(ys)

class View:
    def __init__(self, ox, oy, s, label=None, sub=None):
        self.ox, self.oy, self.s, self.label, self.sub = ox, oy, s, label, sub
    def P(self, x, y): return (self.ox + self.s * x, self.oy - self.s * y)

def fit(names, cx, cy, sc):
    """View with the union bbox of the named projections centred on (cx, cy)."""
    polys = [p for n in names for p in load(n)]
    x0, y0, x1, y1 = bbox(polys)
    v = View(cx - sc * (x0 + x1) / 2, cy + sc * (y0 + y1) / 2, sc)
    v.top = cy - sc * (y1 - y0) / 2; v.bot = cy + sc * (y1 - y0) / 2
    v.left = cx - sc * (x1 - x0) / 2; v.right = cx + sc * (x1 - x0) / 2
    return v

def path(view, polys, stroke=INK, sw=1.4, dash=None, fill='none', op=1):
    d = []
    for pl in polys:
        pts = [view.P(*p) for p in pl]
        d.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z')
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="{" ".join(d)}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linejoin="round"{da} opacity="{op}"/>')

def T(x, y, s, size=13, anchor='middle', color=INK, weight='normal', font=FONT, rot=0, ls=0.6):
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}" font-weight="{weight}" letter-spacing="{ls}"{tr}>{html.escape(str(s))}</text>')

def L(x1, y1, x2, y2, c=THIN, w=0.9, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"{da}/>'

def arrow(x, y, ang, c=THIN, size=8):
    a = math.radians(ang)
    p1 = (x - size * math.cos(a - 0.3), y - size * math.sin(a - 0.3))
    p2 = (x - size * math.cos(a + 0.3), y - size * math.sin(a + 0.3))
    return f'<path d="M{x:.1f},{y:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z" fill="{c}"/>'

def dim(v, p1, p2, off, text=None, orient='h', c=THIN, size=12):
    """Linear dimension between model points p1, p2 in view v; off in mm (perpendicular)."""
    x1, y1 = v.P(*p1); x2, y2 = v.P(*p2); o = off * v.s; out = []
    if orient == 'h':
        yy = (min(y1, y2) - o) if off > 0 else (max(y1, y2) - o)
        out += [L(x1, y1, x1, yy - (4 if off > 0 else -4), c, 0.6), L(x2, y2, x2, yy - (4 if off > 0 else -4), c, 0.6),
                L(x1, yy, x2, yy, c, 0.8)]
        d = abs(x2 - x1); val = abs(p2[0] - p1[0])
        if d > 26: out += [arrow(x1, yy, 180, c), arrow(x2, yy, 0, c)] if x2 > x1 else [arrow(x1, yy, 0, c), arrow(x2, yy, 180, c)]
        else: out += [arrow(min(x1, x2), yy, 0, c), arrow(max(x1, x2), yy, 180, c)]
        out.append(T((x1 + x2) / 2, yy - 4, text or f'{val:g}', size, color=INK))
    else:
        xx = (max(x1, x2) + o) if off > 0 else (min(x1, x2) + o)
        out += [L(x1, y1, xx + (4 if off > 0 else -4), y1, c, 0.6), L(x2, y2, xx + (4 if off > 0 else -4), y2, c, 0.6),
                L(xx, y1, xx, y2, c, 0.8)]
        val = abs(p2[1] - p1[1])
        out += [arrow(xx, max(y1, y2), 90, c), arrow(xx, min(y1, y2), -90, c)] if abs(y2 - y1) > 26 else \
               [arrow(xx, min(y1, y2), 90, c), arrow(xx, max(y1, y2), -90, c)]
        tx = xx + (5 if off > 0 else -5); ty = (y1 + y2) / 2
        out.append(T(tx, ty, text or f'{val:g}', size, color=INK, rot=-90 if True else 0))
    return ''.join(out)

def leader(v, p, text, dx, dy, size=12, c=THIN):
    """Leader from a model point to a note offset (dx, dy) in sheet units."""
    x, y = v.P(*p); tx, ty = x + dx, y + dy
    anc = 'start' if dx >= 0 else 'end'
    return (L(x, y, tx, ty, c, 0.7) + f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="{c}"/>' +
            L(tx, ty, tx + (6 if dx >= 0 else -6), ty, c, 0.7) +
            T(tx + (9 if dx >= 0 else -9), ty + 4, text, size, anchor=anc))

def balloon(num, ax, ay, bx, by, r=13):
    return (L(ax, ay, bx, by, ACC, 0.8) + f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="2.4" fill="{ACC}"/>' +
            f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r}" fill="{BG}" stroke="{ACC}" stroke-width="1.4"/>' +
            T(bx, by + 4.5, num, 13, color=ACC, weight='bold', ls=0))

def view_title(v, x, y, title, scale):
    return T(x, y, title, 15, weight='bold', ls=1.5) + T(x, y + 16, f'SCALE {scale}', 11, color=THIN, ls=1)

def crosshair(v, x=0, y=0, n=8):
    X, Y = v.P(x, y)
    return L(X - n, Y, X + n, Y, FAINT, 0.6, '6 2 1 2') + L(X, Y - n, X, Y + n, FAINT, 0.6, '6 2 1 2')

# ---------------------------------------------------------------- sheet frame
def frame(title, dwg_no, sheet, scale='AS NOTED', subtitle=''):
    g = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>']
    # faint grid
    for x in range(40, W - 39, 20): g.append(L(x, 40, x, H - 40, GRID, 0.5))
    for y in range(40, H - 39, 20): g.append(L(40, y, W - 40, y, GRID, 0.5))
    g.append(f'<rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="{INK}" stroke-width="1"/>')
    g.append(f'<rect x="40" y="40" width="{W-80}" height="{H-80}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    # zone ticks
    for i, x in enumerate(range(40, W - 40, (W - 80) // 8)):
        g.append(L(x, 20, x, 40, INK, 0.8)); g.append(L(x, H - 40, x, H - 20, INK, 0.8))
        if i < 8: g.append(T(x + (W - 80) / 16, 34, str(8 - i), 11, color=THIN)); g.append(T(x + (W - 80) / 16, H - 26, str(8 - i), 11, color=THIN))
    for i, y in enumerate(range(40, H - 40, (H - 80) // 6)):
        g.append(L(20, y, 40, y, INK, 0.8)); g.append(L(W - 40, y, W - 20, y, INK, 0.8))
        if i < 6: g.append(T(30, y + (H - 80) / 12 + 4, 'ABCDEF'[i], 11, color=THIN)); g.append(T(W - 30, y + (H - 80) / 12 + 4, 'ABCDEF'[i], 11, color=THIN))
    # title block
    x0, y0, w, h = W - 40 - 600, H - 40 - 150, 600, 150
    g.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{BG}" stroke="{INK}" stroke-width="2"/>')
    g += [L(x0, y0 + 46, x0 + w, y0 + 46, INK, 1.2), L(x0, y0 + 100, x0 + w, y0 + 100, INK, 1),
          L(x0 + 380, y0 + 100, x0 + 380, y0 + h, INK, 1), L(x0 + 480, y0 + 100, x0 + 480, y0 + h, INK, 1),
          L(x0 + 300, y0, x0 + 300, y0 + 46, INK, 1)]
    g.append(T(x0 + 12, y0 + 30, 'KAT-5', 26, anchor='start', weight='bold', ls=4))
    g.append(T(x0 + 150, y0 + 22, '5" FPV QUAD', 12, anchor='start', color=THIN, ls=1.5))
    g.append(T(x0 + 150, y0 + 38, 'PRINTED FRAME', 12, anchor='start', color=THIN, ls=1.5))
    g.append(T(x0 + 312, y0 + 18, 'UNITS: mm   TOL: ±0.2 UNLESS NOTED', 10.5, anchor='start', color=THIN, ls=0.5))
    g.append(T(x0 + 312, y0 + 34, 'PRINTER: BAMBU LAB P1P / P1S', 10.5, anchor='start', color=THIN, ls=0.5))
    g.append(T(x0 + 12, y0 + 72, title, 20, anchor='start', weight='bold', ls=1.5))
    if subtitle: g.append(T(x0 + 12, y0 + 92, subtitle, 12, anchor='start', color=THIN, ls=0.6))
    g.append(T(x0 + 12, y0 + 118, 'DWG NO.', 10, anchor='start', color=THIN, ls=1))
    g.append(T(x0 + 12, y0 + 140, dwg_no, 17, anchor='start', weight='bold', ls=1.5, font=MONO))
    g.append(T(x0 + 220, y0 + 118, 'DATE', 10, anchor='start', color=THIN, ls=1))
    g.append(T(x0 + 220, y0 + 140, DATE, 13, anchor='start', font=MONO))
    g.append(T(x0 + 390, y0 + 118, 'SCALE', 10, anchor='start', color=THIN, ls=1))
    g.append(T(x0 + 390, y0 + 140, scale, 13, anchor='start', font=MONO))
    g.append(T(x0 + 490, y0 + 118, 'SHEET', 10, anchor='start', color=THIN, ls=1))
    g.append(T(x0 + 490, y0 + 140, f'{sheet} OF {N_SHEETS}', 15, anchor='start', weight='bold', font=MONO))
    g.append(T(60, H - 52, 'GENERATED FROM kat5.scad (PARAMETRIC). DRAWING DIMENSIONS ARE NOMINAL CAD VALUES; PRINTED PARTS MAY NEED ±0.2 mm.', 10, anchor='start', color=FAINT, ls=0.5))
    return g

def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">' + ''.join(body) + '</svg>')

def table(x, y, cols, rows, rh=21, head=True, size=11.5):
    """cols: [(title, width, align)]"""
    g = []; tw = sum(c[1] for c in cols)
    g.append(f'<rect x="{x}" y="{y}" width="{tw}" height="{rh*(len(rows)+1)}" fill="{BG}" stroke="{INK}" stroke-width="1.6"/>')
    cx = x
    for title, w_, al in cols:
        g.append(T(cx + (6 if al == 'start' else w_ / 2), y + rh - 6, title, 10.5, anchor=al, weight='bold', color=ACC, ls=1))
        cx += w_
    g.append(L(x, y + rh, x + tw, y + rh, INK, 1.2))
    for i, r in enumerate(rows):
        yy = y + rh * (i + 2)
        g.append(L(x, yy, x + tw, yy, FAINT, 0.5))
        cx = x
        for (title, w_, al), val in zip(cols, r):
            g.append(T(cx + (6 if al == 'start' else w_ / 2), yy - 6, val, size, anchor=al, ls=0.2))
            cx += w_
    cx = x
    for title, w_, al in cols[:-1]:
        cx += w_; g.append(L(cx, y, cx, y + rh * (len(rows) + 1), FAINT, 0.6))
    return g

# ---------------------------------------------------------------- parameters
P = dict(motor_r=115.0, mxy=115 / math.sqrt(2), stack=30.5, so_x=16, so_y=40, body_w=50, body_l=92,
         arm_t=4, plate_t=3, top_t=3, so_h=30, prop_d=129.5)

BOM = [  # item, qty, description, spec / material, file or source
    ('1', '4', 'ARM, BOLT-ON', 'PETG, 6 WALLS, 40% GYROID', 'stl/arm.stl'),
    ('2', '1', 'CENTRE PLATE', 'PETG, 3 mm', 'stl/bottom_plate.stl'),
    ('3', '1', 'TOP PLATE', 'PETG, 3 mm', 'stl/top_plate.stl'),
    ('4', '1', 'CANOPY', 'PETG/PLA 1.2 mm (or TPU)', 'stl/canopy.stl'),
    ('5', '1', 'GPS + XT60 TOWER', 'PETG', 'stl/gps_xt60_mount.stl'),
    ('6', '1', 'CAMERA MOUNT', 'TPU 95A', 'stl/cam_mount.stl'),
    ('7', '1', 'ANTENNA MOUNT', 'TPU 95A', 'stl/antenna_mount.stl'),
    ('8', '1', 'GOPRO MOUNT', 'TPU 95A', 'stl/gopro_mount.stl'),
    ('9', '1', 'VTX PLATE', 'PETG, 1.6 mm', 'stl/vtx_plate.stl'),
    ('10', '4', 'STANDOFF M3 x 30', 'ALUMINIUM, 5–5.5 HEX', 'BUY'),
    ('11', '4', 'MOTOR 2207 1750–1950 KV', 'e.g. iFlight XING2 2207', 'Ø29.1 x 19.1'),
    ('12', '4', 'PROP 5.1" TRI-BLADE', 'e.g. 5.1 x 3.6 x 3', 'Ø129.5'),
    ('13', '1', 'ESC 4-IN-1 55 A', 'SpeedyBee BLS 55A 30x30', '45.6 x 44 x 8'),
    ('14', '1', 'VTX 5.8 GHz 800 mW', 'SpeedyBee TX800 20x20', '28 x 28'),
    ('15', '1', 'FPV CAMERA', 'Caddx Ratel 2 (19 mm)', '19 x 19 x 20'),
    ('16', '1', 'GPS + COMPASS', 'Matek M10Q-5883', '20 x 20 x 12.4'),
    ('17', '1', 'XT60 PIGTAIL (FEMALE)', '12 AWG, to ESC', '15.8 x 8.2 x 16'),
    ('18', '1', 'BATTERY 6S 1100–1200', 'e.g. Tattu R-Line 1200', '78 x 40 x 34 MAX'),
    ('19', '1', 'RECEIVER ELRS 2.4 GHz', 'Radiomaster RP1/RP2', '13 x 11 x 3'),
    ('20', '2', 'BATTERY STRAP 20 mm', 'NON-SLIP', '—'),
    ('21', '1', 'FLIGHT CONTROLLER F405', 'SpeedyBee F405 V4', '41.6 x 39.4 x 7.8'),
]
FASTENERS = [
    ('16', 'M3 x 8 SHCS', 'MOTOR → ARM (4 mm THREAD IN MOTOR)'),
    ('8', 'M3 x 10 + NYLOCK', 'ARM → CENTRE PLATE'),
    ('4', 'M3 x 30–35 + NYLOCK', 'STACK BOLTS THROUGH ARM ROOTS'),
    ('8', 'M3 x 8', 'STANDOFFS TOP + BOTTOM'),
    ('2', 'M3 x 10 + NYLOCK', 'TOWER → TOP PLATE TAB'),
    ('2', 'M2 x 6', 'CAMERA PIVOT'),
    ('4', 'M2 NYLON + 1.5 mm SPACER', 'VTX → VTX PLATE'),
    ('1', 'M5 THUMBSCREW', 'GOPRO'),
]

FRAME_PARTS = ['arm', 'bottom_plate', 'cam_mount', 'antenna_mount', 'canopy', 'top_plate', 'gopro_mount', 'gps_xt60_mount', 'vtx_plate', 'standoffs']
COMPS = ['esc', 'fc', 'vtx', 'camera', 'motors', 'props', 'battery', 'gps', 'xt60']

def assembly_view(v, view, show_props=True):
    g = []
    for c in COMPS:
        if c == 'props' and not show_props: continue
        g.append(path(v, load(f'comp_{c}_{view}_all'), stroke=FAINT if c != 'props' else '#8fb4e6', sw=0.9,
                      dash='5 3' if c != 'props' else '10 4 2 4'))
    for f in FRAME_PARTS:
        g.append(path(v, load(f'placed_{f}_{view}_all'), stroke=INK, sw=1.3))
    return g

# ================================================================ SHEET 1: GA
def sheet1():
    g = frame('GENERAL ARRANGEMENT', 'K5-100', 1, '1:2', 'ASSEMBLY — TOP / FRONT / SIDE')
    s = 2.05
    top = View(410, 480, s)
    g += assembly_view(top, 'top'); g.append(crosshair(top))
    g.append(view_title(top, 410, 90, 'TOP VIEW', '1:2'))
    m = P['mxy']
    g.append(dim(top, (-m, m), (m, m), 82, '162.6'))
    g.append(dim(top, (m, -m), (m, m), 82, '162.6', orient='v'))
    # diagonal wheelbase
    a, b = top.P(-m, -m), top.P(m, m)
    g.append(L(*a, *b, ACC, 0.8, '8 4')); q = (a[0] * 0.8 + b[0] * 0.2, a[1] * 0.8 + b[1] * 0.2); g.append(T(q[0] + 14, q[1] - 6, 'WHEELBASE 230 (DIAG.)', 12, color=ACC, rot=-45))
    g.append(dim(top, (-25, -46), (25, -46), -88, '50'))
    g.append(leader(top, (15 + 7.07, 36 + 7.07), 'PROP TIP ↔ BODY 5.6 MIN.', 150, -40, 11))
    g.append(leader(top, (0, 50), 'FRONT (CAMERA)', -20, -80, 11))
    # balloons on top view
    for n, p, dx, dy in [('1', (m * 0.55, -m * 0.55), 70, 60), ('11', (m, m), 55, -40), ('12', (-m - 40, -m - 40), -40, 30),
                         ('3', (-20, 10), -150, 70), ('5', (0, -78), -80, 60), ('8', (0, 40), 110, -95)]:
        ax, ay = top.P(*p); g.append(balloon(n, ax, ay, ax + dx, ay + dy))
    # FRONT view (looking aft, X horizontal, Z up)
    fr = View(1170, 300, s)
    g += assembly_view(fr, 'front')
    g.append(view_title(fr, 1170, 90, 'FRONT VIEW', '1:2'))
    g.append(dim(fr, (-m, 0), (m, 0), -24, '162.6'))
    g.append(dim(fr, (-25, 0), (-25, 78), -100, '78', orient='v'))
    g.append(leader(fr, (0, 78), 'TOP OF BATTERY', 120, -20, 11))
    for n, p, dx, dy in [('15', (0, 21), 0, 0), ('4', (24, 20), 95, 30), ('18', (-15, 70), -110, -30), ('13', (-22, 11), -150, 20)]:
        if n == '15': continue
        ax, ay = fr.P(*p); g.append(balloon(n, ax, ay, ax + dx, ay + dy))
    # SIDE view (Y horizontal, front to the right, Z up)
    sd = View(1170, 720, s)
    g += assembly_view(sd, 'side')
    g.append(view_title(sd, 1170, 470, 'SIDE VIEW (FRONT →)', '1:2'))
    g.append(dim(sd, (-84, 0), (46, 0), -24, '130'))
    g.append(dim(sd, (46, 4), (46, 42), 20, '38', orient='v'))
    g.append(leader(sd, (-69, 79.4), 'GPS ABOVE BATTERY', -80, -30, 11))
    for n, p, dx, dy in [('5', (-80, 50), -60, 40), ('6', (40, 10), 90, 50), ('7', (-44, 20), -70, 60), ('16', (-69, 73), 40, -55), ('17', (-76, 48), -110, 10),
                         ('2', (0, 5.5), 30, 70), ('10', (40, 25), 140, -40)]:
        ax, ay = sd.P(*p); g.append(balloon(n, ax, ay, ax + dx, ay + dy))
    # notes
    notes = ['NOTES',
             '1. SOLID LINES: PRINTED / FRAME PARTS. DASHED: BOUGHT COMPONENTS AT PUBLISHED SIZE.',
             '2. CHAIN LINE: 5.1" PROP DISC, Ø129.5.',
             '3. BALLOON NUMBERS REFER TO THE PARTS LIST ON SHEET 2.',
             '4. ARMS MOUNT UNDER THE CENTRE PLATE; 3 x M3 PER ARM, ONE IS A STACK BOLT.',
             '5. FIT CHECKED IN CAD AGAINST REAL PART SIZES — SEE SHEET 7.']
    for i, t in enumerate(notes):
        g.append(T(70, 905 + i * 18, t, 12 if i else 13, anchor='start', weight='bold' if i == 0 else 'normal', color=INK if i else ACC))
    return svg(g)

# ================================================================ SHEET 2: exploded + BOM
def sheet2():
    g = frame('EXPLODED ASSEMBLY + PARTS LIST', 'K5-101', 2, 'NTS', 'ISOMETRIC — NOT TO SCALE')
    img = base64.b64encode(open(os.path.join(HERE, 'iso_lines.png'), 'rb').read()).decode()
    ix, iy, iw = 60, 60, 760
    sc = iw / 1600; ih = 1700 * sc
    g.append(f'<image x="{ix}" y="{iy}" width="{iw}" height="{ih:.0f}" xlink:href="data:image/png;base64,{img}"/>')
    g.append(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih:.0f}" fill="none" stroke="{FAINT}" stroke-width="0.6"/>')
    anch = json.load(open(os.path.join(HERE, 'anchors.json')))
    # place balloons in two columns at the image edges, sorted by height
    items = sorted(((int(k), ix + v[0] * sc, iy + v[1] * sc) for k, v in anch.items()), key=lambda t: t[2])
    left = [t for t in items if t[1] < ix + iw * 0.5]; right = [t for t in items if t[1] >= ix + iw * 0.5]
    def column(lst, bx):
        out = []; last = -1e9
        for n, ax, ay in lst:
            by = max(ay, last + 32); last = by
            out.append(balloon(str(n), ax, ay, bx, by))
        return out
    g += column(left, ix + 22); g += column(right, ix + iw - 22)
    g.append(T(ix + 10, iy + ih + 22, 'EXPLODED ISOMETRIC', 15, anchor='start', weight='bold', ls=1.5))
    # parts list
    cols = [('ITEM', 46, 'middle'), ('QTY', 42, 'middle'), ('DESCRIPTION', 230, 'start'), ('SPEC / MATERIAL', 230, 'start'), ('FILE / SIZE (mm)', 236, 'start')]
    g.append(T(860, 82, 'PARTS LIST', 16, anchor='start', weight='bold', ls=2))
    g += table(860, 92, cols, BOM, rh=22)
    g.append(T(860, 92 + 22 * (len(BOM) + 1) + 34, 'FASTENERS', 16, anchor='start', weight='bold', ls=2))
    g += table(860, 92 + 22 * (len(BOM) + 1) + 44, [('QTY', 46, 'middle'), ('SIZE', 220, 'start'), ('WHERE', 518, 'start')], FASTENERS, rh=21)
    return svg(g)

# ================================================================ SHEET 3: arm + centre plate
def sheet3():
    g = frame('ARM + CENTRE PLATE', 'K5-201', 3, '1:1', 'ITEMS 1, 2 — PETG')
    s = 4.0
    v = View(240, 270, s)
    g += [path(v, load('part_arm_top_all')), path(v, load('part_arm_top_4.01'), stroke=INK, sw=1.0)]
    g.append(view_title(v, 500, 100, 'ITEM 1 — ARM, TOP VIEW', '1:1'))
    g.append(L(*v.P(-2, 0), *v.P(133, 0), FAINT, 0.6, '14 3 2 3'))
    g.append(dim(v, (3, 0), (131, 0), 30, '128'))
    g.append(dim(v, (21.57, 0), (115, 0), -26, '93.4'))
    g.append(dim(v, (21.57, 0), (31, 6), 20, '9.4'))
    g.append(dim(v, (31, -6), (31, 6), -18, '12', orient='v'))
    g.append(dim(v, (99, -8), (99, 8), -12, '16', orient='v'))
    g.append(dim(v, (107, 8), (123, 8), 12, '16'))
    g.append(leader(v, (21.57 - 1.2, 1.2), 'Ø3.3 STACK BOLT (30.5 SQ.)', -40, -95, 11))
    g.append(leader(v, (31, -6), '2x Ø3.3 ARM BOLTS', -60, 80, 11))
    g.append(leader(v, (115, 0), 'Ø7.5 SHAFT CLEARANCE', 70, -130, 11))
    g.append(leader(v, (123, 8), '4x Ø3.3 ON 16x16 (M3 MOTOR)', 60, -60, 11))
    g.append(leader(v, (127, -9), 'MOTOR PAD Ø32', 50, 55, 11))
    g.append(dim(v, (3, -11), (3, 11), -8, '22', orient='v'))
    g.append(leader(v, (82, -6.6), 'MOTOR-WIRE ZIP SLOTS 3.2 x 1.8', 30, 125, 11))
    g.append(leader(v, (60, 3.2), 'SPINE (RAISED)', 10, -70, 11))
    # side elevation
    e = View(240, 560, s)
    g += [path(e, load('part_arm_front_all'))]
    g.append(view_title(e, 500, 418, 'ARM — SIDE ELEVATION', '1:1'))
    g.append(dim(e, (3, 0), (3, 4), -10, '4', orient='v'))
    g.append(dim(e, (50, 4), (50, 12), 8, '8', orient='v'))
    g.append(dim(e, (41, 4), (41, 9), -6, '5', orient='v'))
    g.append(dim(e, (98, 4), (98, 7), 10, '3', orient='v'))
    g.append(dim(e, (41, 12), (98, 12), 10, '57 (SPINE 41 → 98 FROM CENTRE)'))
    g.append(leader(e, (75, 9), 'SPINE BASE W 8 → TOP W 4 (FILLETED)', 30, 40, 11))
    # centre plate
    cp = View(1290, 430, 3.6)
    g += [path(cp, load('part_bottom_plate_top_all')), crosshair(cp)]
    g.append(view_title(cp, 1290, 90, 'ITEM 2 — CENTRE PLATE, TOP VIEW', '≈ 1:1.1'))
    g.append(dim(cp, (-25, 46), (25, 46), 14, '50'))
    g.append(dim(cp, (-25, -46), (-25, 46), -46, '92', orient='v'))
    g.append(dim(cp, (-15.25, -15.25), (15.25, -15.25), -50, '30.5'))
    g.append(dim(cp, (15.25, -15.25), (15.25, 15.25), 48, '30.5', orient='v'))
    g.append(dim(cp, (-16, -40), (16, -40), -30, '32'))
    g.append(dim(cp, (16, -40), (16, 40), 30, '80', orient='v'))
    g.append(leader(cp, (0, -7), 'Ø14 CENTRE', 90, 160, 11))
    g.append(leader(cp, (31 * 0.7071 + 6 * 0.7071, 31 * 0.7071 - 6 * 0.7071), '8x Ø3.3 ARM BOLTS (R31, ±6)', 70, 120, 11))
    g.append(leader(cp, (-16, -40), '4x Ø3.3 STANDOFFS', -40, 95, 11))
    g.append(leader(cp, (-23, 30), 'R10 BODY CORNERS, R6 FILLETS', -60, -110, 11))
    g.append(T(1290, 760, 'THICKNESS 3.0 — ARMS BOLT TO THE UNDERSIDE', 12, color=THIN))
    notes = ['PRINT NOTES (ITEMS 1, 2)', '• PETG 0.2 mm LAYERS, 6 WALLS, 5 TOP/BOTTOM, 40% GYROID.',
             '• PRINT FLAT, SPINE UP. NO SUPPORTS.', '• PRINT 4 ARMS + 2 SPARES. ALL ARMS ARE IDENTICAL.',
             '• ALL HOLES Ø3.3 FOR M3 UNLESS NOTED. CHECK FIT ON THE TEST COUPON FIRST.']
    for i, t in enumerate(notes):
        g.append(T(70, 760 + i * 19, t, 12.5 if i else 13, anchor='start', weight='bold' if i == 0 else 'normal', color=ACC if i == 0 else INK))
    return svg(g)

# ================================================================ SHEET 4: top plate + canopy
def vt(v, title, scale, dy=58):
    return view_title(v, (v.left + v.right) / 2, v.top - dy, title, scale)

def sheet4():
    g = frame('TOP PLATE + CANOPY', 'K5-202', 4, 'AS NOTED', 'ITEMS 3, 4')
    tp = fit(['part_top_plate_top_all'], 330, 540, 3.6)
    g += [path(tp, load('part_top_plate_top_all')), crosshair(tp)]
    g.append(vt(tp, 'ITEM 3 — TOP PLATE', '≈ 1:1.1', 150))
    g.append(dim(tp, (-25, 46), (25, 46), 26, '50'))
    g.append(dim(tp, (-21.5, 26), (21.5, 26), 24, '43 (STRAP SLOT C/C)'))
    g.append(dim(tp, (-25, -66), (-25, 46), -30, '112', orient='v'))
    g.append(dim(tp, (25, -46), (25, 46), 22, '92', orient='v'))
    g.append(dim(tp, (21.5, 4), (21.5, 26), 8, '22', orient='v'))
    g.append(dim(tp, (-8, -58), (8, -58), -16, '16'))
    g.append(dim(tp, (-14, -66), (14, -66), -26, '28 (TAB)'))
    g.append(leader(tp, (21.5, -15), '4x STRAP SLOTS 22 x 3.5 (20 mm STRAPS)', 110, 50, 11))
    g.append(leader(tp, (0, 29), 'GOPRO STRAP SLOT 19 x 3.5', 150, -40, 11))
    g.append(leader(tp, (0, -6), 'WIRE PASS 16 x 28', 150, 0, 11))
    g.append(leader(tp, (8, -58), '2x Ø3.3 TOWER BOLTS', 110, 20, 11))
    g.append(leader(tp, (-16, -40), '4x Ø3.3 STANDOFFS (32 x 80)', -40, 140, 11))
    g.append(T((tp.left + tp.right) / 2, tp.bot + 120, 'THICKNESS 3.0', 12, color=THIN))
    cf = fit(['part_canopy_front_all'], 900, 300, 3.6)
    g += [path(cf, load('part_canopy_front_all'))]
    g.append(vt(cf, 'ITEM 4 — CANOPY, FRONT', '≈ 1:1.1', 80))
    g.append(dim(cf, (-25, 32), (25, 32), 10, '50'))
    g.append(dim(cf, (25, 0), (25, 32), 10, '32', orient='v'))
    g.append(dim(cf, (-14, 3), (14, 3), -12, '28 (CAMERA WINDOW)'))
    g.append(dim(cf, (-25, 3), (-25, 29), -10, '26', orient='v'))
    cs = fit(['part_canopy_side_all'], 1360, 300, 3.6)
    g += [path(cs, load('part_canopy_side_all'))]
    g.append(vt(cs, 'CANOPY — SIDE (FRONT →)', '≈ 1:1.1', 80))
    g.append(dim(cs, (-46, 32), (46, 32), 10, '92'))
    g.append(dim(cs, (-8, 8), (8, 8), -18, '16 (USB)'))
    g.append(dim(cs, (8, 8), (8, 20), 12, '12', orient='v'))
    g.append(leader(cs, (-34, 16), 'VENTS 3 x 16 @ 25°', -40, 95, 11))
    g.append(leader(cs, (-25, 4), 'MOTOR-WIRE EXITS 14 x 9 (4 CORNERS)', 10, 120, 11))
    ct = fit(['part_canopy_top_all'], 1000, 690, 2.6)
    g += [path(ct, load('part_canopy_top_all'))]
    g.append(vt(ct, 'CANOPY — TOP', '≈ 1:1.5', 40))
    g.append(leader(ct, (24.4, 0), 'WALL 1.2', 60, 0, 11))
    g.append(leader(ct, (24.4, 25), 'ENGRAVED "KAT-5" BOTH SIDES, 0.6 DEEP', 60, -40, 11))
    notes = ['PRINT NOTES', '• TOP PLATE: PETG FLAT, 6 WALLS, 40%.', '• CANOPY: PETG/PLA UPRIGHT, 3 WALLS, NO SUPPORTS.',
             '  TPU IF YOU CRASH A LOT.', '• CANOPY NEEDS ALU STANDOFFS ≤ 5.5 HEX.']
    for i, t in enumerate(notes):
        g.append(T(70, 930 + i * 19, t, 12.5, anchor='start', weight='bold' if i == 0 else 'normal', color=ACC if i == 0 else INK))
    return svg(g)

# ================================================================ SHEET 5: tower + mounts
def sheet5():
    g = frame('TOWER, MOUNTS, VTX PLATE', 'K5-203', 5, 'AS NOTED', 'ITEMS 5–9')
    s = 5.0
    tf = fit(['part_gps_xt60_mount_front_all'], 230, 300, s)
    g += [path(tf, load('part_gps_xt60_mount_front_all'))]
    g.append(vt(tf, 'ITEM 5 — TOWER, REAR', '≈ 1.25:1', 105))
    g.append(dim(tf, (-14, 28), (14, 28), 12, '28'))
    g.append(dim(tf, (14, 0), (14, 28), 12, '28', orient='v'))
    g.append(dim(tf, (-8.15, 2), (8.15, 2), -14, '16.3 (XT60 15.8)'))
    g.append(dim(tf, (-11, 2), (-11, 10.5), -12, '8.5', orient='v'))
    g.append(leader(tf, (0, 6), 'XT60 SOCKET FACES REAR', 0, 0, 1) if False else '')
    ts = fit(['part_gps_xt60_mount_side_all'], 560, 300, s)
    g += [path(ts, load('part_gps_xt60_mount_side_all'))]
    g.append(vt(ts, 'TOWER — SIDE (FRONT →)', '≈ 1.25:1', 105))
    g.append(dim(ts, (-84, 0), (-54.5, 0), -14, '29.5'))
    g.append(dim(ts, (-54.5, 0), (-54.5, 25), 14, '25 (GPS FLOOR)', orient='v'))
    tt = fit(['part_gps_xt60_mount_top_all'], 880, 300, s)
    g += [path(tt, load('part_gps_xt60_mount_top_all')), path(tt, load('part_gps_xt60_mount_top_24.6'), sw=1.0)]
    g.append(vt(tt, 'TOWER — TOP (GPS POCKET)', '≈ 1.25:1', 105))
    g.append(dim(tt, (-10.3, -58.95), (10.3, -58.95), 14, '20.6 (GPS 20)'))
    g.append(dim(tt, (-8, -58), (8, -58), -16, '16 (M3)') if False else '')
    g.append(leader(tt, (0, -60.5), '2x ZIP-TIE SLOTS', 90, 60, 11))
    cmt = fit(['part_cam_mount_top_all'], 1200, 300, s)
    g += [path(cmt, load('part_cam_mount_top_all')), path(cmt, load('part_cam_mount_top_2.01'), sw=1.0)]
    g.append(vt(cmt, 'ITEM 6 — CAMERA MOUNT (TPU)', '≈ 1.25:1', 145))
    g.append(dim(cmt, (-9.7, 46), (9.7, 46), 10, '19.4 (CAMERA 19)'))
    g.append(dim(cmt, (-16, 31), (16, 31), -14, '32 (M3)'))
    cm = fit(['part_cam_mount_side_all'], 1480, 300, s)
    g += [path(cm, load('part_cam_mount_side_all'))]
    g.append(T((cm.left + cm.right) / 2, cm.top - 30, 'SIDE', 13, weight='bold', ls=1))
    g.append(dim(cm, (46, 0), (46, 14), 12, '14', orient='v'))
    g.append(leader(cm, (37, 14), 'Ø2.2 M2 PIVOT', 40, -60, 11))
    gp = fit(['part_gopro_mount_side_all'], 230, 700, s)
    g += [path(gp, load('part_gopro_mount_side_all'))]
    g.append(vt(gp, 'ITEM 8 — GOPRO MOUNT (TPU)', '≈ 1.25:1', 70))
    g.append(T((gp.left + gp.right) / 2, gp.bot + 34, '3 PRONGS x 3.0, GAP 3.2, Ø5.3 (M5), TILT 20°', 11, color=THIN))
    vp = fit(['part_vtx_plate_top_all'], 560, 700, 4.0)
    g += [path(vp, load('part_vtx_plate_top_all')), crosshair(vp)]
    g.append(vt(vp, 'ITEM 9 — VTX PLATE', '1:1', 70))
    g.append(dim(vp, (-15.25, -15.25), (15.25, -15.25), -14, '30.5'))
    g.append(dim(vp, (-10, 10), (10, 10), 14, '20'))
    g.append(T(560, vp.bot + 70, 'Ø3.3 ON 30.5 SQ. · Ø2.2 ON 20 SQ. · 1.6 THK', 11, color=THIN))
    am = fit(['part_antenna_mount_side_all'], 900, 700, 4.0)
    g += [path(am, load('part_antenna_mount_side_all'))]
    g.append(vt(am, 'ITEM 7 — ANTENNA MOUNT (TPU)', '1:1', 70))
    g.append(T((am.left + am.right) / 2, am.bot + 34, 'Ø6.6 SMA BULKHEAD · 2x Ø2.4 ELRS TUBES @ 45°', 11, color=THIN))
    at = fit(['part_antenna_mount_top_all'], 1230, 700, 4.0)
    g += [path(at, load('part_antenna_mount_top_all')), path(at, load('part_antenna_mount_top_2.01'), sw=1.0)]
    g.append(T((at.left + at.right) / 2, at.top - 62, 'TOP', 13, weight='bold', ls=1))
    g.append(dim(at, (-16, -40), (16, -40), 12, '32 (M3)'))
    return svg(g)

# ================================================================ SHEET 6: wiring
def box(x, y, w, h, title, sub=None, c=INK):
    g = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#123f7c" stroke="{c}" stroke-width="1.8"/>',
         T(x + w / 2, y + 22, title, 14, weight='bold', ls=1.2)]
    if sub: g.append(T(x + w / 2, y + 38, sub, 10.5, color=THIN))
    return g

def pad(x, y, name, side='r', c=INK):
    g = [f'<rect x="{x-4}" y="{y-4}" width="8" height="8" fill="{c}"/>']
    g.append(T(x + (-10 if side == 'r' else 10), y + 4, name, 10.5, anchor='end' if side == 'r' else 'start', font=MONO, ls=0))
    return g

def wire(pts, c, w=2.2, label=None, dash=None):
    d = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ''
    g = [f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round"{da}/>']
    if label:
        (x1, y1), (x2, y2) = pts[len(pts) // 2 - 1], pts[len(pts) // 2]
        g.append(T((x1 + x2) / 2, (y1 + y2) / 2 - 5, label, 9.5, color=c, font=MONO, ls=0))
    return g

C_RED, C_BLK, C_YEL, C_GRN, C_WHT, C_BLU, C_ORG, C_VIO = '#ff6b6b', '#c9d2dc', '#ffd84d', '#5fe08a', '#ffffff', '#6fc3ff', '#ffa24d', '#d39bff'

def sheet6():
    g = frame('WIRING DIAGRAM', 'K5-300', 6, 'NTS', 'SpeedyBee F405 V4 STACK — ARDUPILOT')
    BX, BW = 60, 210
    # power path
    g += box(BX, 100, BW, 66, 'BATTERY 6S', '22.2 V · 1100–1200 mAh')
    g += box(BX, 220, BW, 56, 'XT60 · ITEM 17', 'ON TOWER · 12 AWG PIGTAIL')
    g += wire([(130, 166), (130, 220)], C_RED, 3.5); g += wire([(200, 166), (200, 220)], C_BLK, 3.5)
    g += box(BX, 330, BW, 56, 'CAPACITOR', '35 V 1000 µF LOW-ESR')
    ex, ey, ew, eh = 340, 220, 300, 280
    g += box(ex, ey, ew, eh, 'ESC 4-IN-1 · ITEM 13', 'SpeedyBee BLS 55A (BLHeli_S)')
    g += pad(ex + 14, ey + 70, 'BAT+', 'l'); g += pad(ex + 14, ey + 100, 'BAT−', 'l')
    g += wire([(130, 276), (130, 296), (ex + 14, 296), (ex + 14, ey + 70)], C_RED, 3.5)
    g += wire([(200, 276), (200, 286), (310, 286), (310, ey + 100), (ex + 14, ey + 100)], C_BLK, 3.5)
    g += wire([(130, 330), (130, 306), (300, 306), (300, ey + 70), (ex + 14, ey + 70)], C_RED, 1.6)
    g += wire([(200, 330), (200, 316), (290, 316), (290, ey + 100)], C_BLK, 1.6)
    g.append(T(BX + BW / 2, 408, 'SOLDER CAP ACROSS ESC BATTERY PADS', 10, color=THIN))
    # motor pads with labelled 3-wire stubs
    mpads = [('M2', 'FR', 'ArduPilot M1 · CCW', 60), ('M4', 'FL', 'ArduPilot M3 · CW', 115), ('M1', 'RR', 'ArduPilot M4 · CW', 170), ('M3', 'RL', 'ArduPilot M2 · CCW', 225)]
    for pn, pos_, ap, dy in mpads:
        y = ey + dy + 20; x = ex + ew - 14
        g += pad(x, y, pn, 'r')
        for o in (-4, 0, 4): g += wire([(x, y + o), (x + 90, y + o)], C_ORG, 1.3)
        g.append(T(x + 98, y - 2, f'TO {pos_} MOTOR', 11.5, anchor='start', weight='bold', color=C_ORG, ls=0.5))
        g.append(T(x + 98, y + 13, ap, 10.5, anchor='start', color=THIN, font=MONO, ls=0))
    # 8-pin harness
    fx, fy, fw, fh = 340, 620, 300, 340
    g += box(fx, fy, fw, fh, 'FLIGHT CONTROLLER · ITEM 21', 'SpeedyBee F405 V4 (ArduPilot)')
    for i, n in enumerate(['VBAT', 'GND', 'CURR', 'TLM', 'M1', 'M2', 'M3', 'M4']):
        x = ex + 42 + i * 31
        g += wire([(x, ey + eh), (x, fy)], C_RED if n == 'VBAT' else (C_BLK if n == 'GND' else C_WHT), 1.6)
        g.append(f'<rect x="{x-11}" y="{ey+eh+22}" width="22" height="52" fill="{BG}"/>')
        g.append(T(x + 4, ey + eh + 48, n, 9.5, font=MONO, ls=0, rot=-90))
    g.append(T(ex + ew / 2, fy - 12, '8-PIN JST-SH HARNESS (SUPPLIED WITH STACK)', 10.5, color=THIN))
    LP = {'5V': fy + 80, 'GND': fy + 102, 'R2': fy + 124, 'T2': fy + 146, '5V.': fy + 190, 'GND.': fy + 212, 'R6': fy + 234, 'T6': fy + 256, 'SDA': fy + 278, 'SCL': fy + 300}
    for n, y in LP.items(): g += pad(fx + 14, y, n.rstrip('.'), 'l')
    RP = {'5V': fy + 80, 'GND': fy + 102, 'CAM': fy + 124, '5V.': fy + 180, 'GND.': fy + 202, 'VTX': fy + 224, 'T3': fy + 246, 'BZ+': fy + 296, 'BZ−': fy + 318}
    for n, y in RP.items(): g += pad(fx + fw - 14, y, n.rstrip('.'), 'r')
    # receiver
    ry = 600; g += box(BX, ry, BW, 118, 'RECEIVER · ITEM 19', 'Radiomaster RP1 ELRS')
    rp = [('5V', C_RED, '5V'), ('GND', C_BLK, 'GND'), ('TX', C_YEL, 'R2'), ('RX', C_GRN, 'T2')]
    for i, (n, c, to) in enumerate(rp):
        y = ry + 56 + i * 16; xr = BX + BW - 14; g += pad(xr, y, n, 'r')
        lane = 320 - i * 10
        g += wire([(xr, y), (lane, y), (lane, LP[to]), (fx + 14, LP[to])], c, 1.6)
    # GPS
    gy = 780; g += box(BX, gy, BW, 150, 'GPS · ITEM 16', 'Matek M10Q-5883')
    gp = [('5V', C_RED, '5V.'), ('GND', C_BLK, 'GND.'), ('TX', C_YEL, 'R6'), ('RX', C_GRN, 'T6'), ('SDA', C_BLU, 'SDA'), ('SCL', C_VIO, 'SCL')]
    for i, (n, c, to) in enumerate(gp):
        y = gy + 56 + i * 15; xr = BX + BW - 14; g += pad(xr, y, n, 'r')
        lane = 326 - i * 8
        g += wire([(xr, y), (lane, y), (lane, LP[to]), (fx + 14, LP[to])], c, 1.6)
    # camera
    cx_, cy_ = 760, 640
    g += box(cx_, cy_, 220, 100, 'CAMERA · ITEM 15', 'Caddx Ratel 2 (5–40 V)')
    for i, (n, c, fr) in enumerate([('5V', C_RED, '5V'), ('GND', C_BLK, 'GND'), ('VID', C_YEL, 'CAM')]):
        y = cy_ + 56 + i * 16; g += pad(cx_ + 14, y, n, 'l')
        lane = 690 + i * 12
        g += wire([(fx + fw - 14, RP[fr]), (lane, RP[fr]), (lane, y), (cx_ + 14, y)], c, 1.6)
    # vtx
    vx, vy = 760, 780
    g += box(vx, vy, 220, 116, 'VTX · ITEM 14', 'SpeedyBee TX800 (3.7–5.5 V)')
    for i, (n, c, fr) in enumerate([('5V', C_RED, '5V.'), ('GND', C_BLK, 'GND.'), ('VID', C_YEL, 'VTX'), ('IRC', C_GRN, 'T3')]):
        y = vy + 56 + i * 16; g += pad(vx + 14, y, n, 'l')
        lane = 690 + i * 12
        g += wire([(fx + fw - 14, RP[fr]), (lane, RP[fr]), (lane, y), (vx + 14, y)], c, 1.6)
    g.append(T(vx + 110, vy + 136, 'MMCX → SMA PIGTAIL TO ITEM 7', 10.5, color=THIN))
    g.append(T(vx + 110, vy + 154, '⚠ 5 V PAD ONLY — NOT 9 V / 10 V', 11, color=ACC, weight='bold'))
    g.append(T(vx + 110, vy + 172, 'VIDEO = FC OSD OUT · IRC = TRAMP CONTROL', 10, color=THIN))
    g.append(T(fx + fw - 60, fy + 340 - 14, 'OPTIONAL BUZZER', 9.5, color=THIN, anchor='end'))
    # Remote ID
    g += box(vx, 962, 220, 52, 'REMOTE ID (US)', 'BROADCAST MODULE · OWN 5 V')
    # motor order figure
    qx, qy, d = 1330, 290, 105
    g.append(T(qx, 92, 'MOTOR ORDER + SPIN — TOP VIEW', 15, weight='bold', ls=1.5))
    g.append(T(qx, 110, 'ARDUPILOT QUAD X · PROPS IN', 11, color=THIN, ls=1))
    pos = {'FL': (qx - d, qy - d), 'FR': (qx + d, qy - d), 'RL': (qx - d, qy + d), 'RR': (qx + d, qy + d)}
    apm = {'FR': (1, 'CCW'), 'RL': (2, 'CCW'), 'FL': (3, 'CW'), 'RR': (4, 'CW')}
    escpad = {'RR': 1, 'FR': 2, 'RL': 3, 'FL': 4}
    g.append(L(qx - d, qy - d, qx + d, qy + d, FAINT, 5)); g.append(L(qx + d, qy - d, qx - d, qy + d, FAINT, 5))
    g.append(f'<rect x="{qx-22}" y="{qy-40}" width="44" height="80" rx="9" fill="#123f7c" stroke="{INK}" stroke-width="1.5"/>')
    g.append(arrow(qx, qy - 52, -90, ACC, 12)); g.append(T(qx, qy - 60, 'FRONT', 11, color=ACC, weight='bold'))
    for k, (x, y) in pos.items():
        n, rot = apm[k]
        g.append(f'<circle cx="{x}" cy="{y}" r="52" fill="none" stroke="#8fb4e6" stroke-width="1" stroke-dasharray="10 4 2 4"/>')
        g.append(f'<circle cx="{x}" cy="{y}" r="21" fill="#123f7c" stroke="{INK}" stroke-width="1.8"/>')
        if rot == 'CCW':
            g.append(f'<path d="M{x+36},{y} A36,36 0 0 0 {x},{y-36}" fill="none" stroke="{ACC}" stroke-width="1.8"/>'); g.append(arrow(x, y - 36, 180, ACC, 9))
        else:
            g.append(f'<path d="M{x-36},{y} A36,36 0 0 1 {x},{y-36}" fill="none" stroke="{ACC}" stroke-width="1.8"/>'); g.append(arrow(x, y - 36, 0, ACC, 9))
        g.append(T(x, y + 5, f'M{n}', 14, weight='bold', ls=0))
        lx = x + (70 if x > qx else -70); anc = 'start' if x > qx else 'end'
        g.append(T(lx, y - 4, f'{k} · {rot}', 11.5, anchor=anc, weight='bold'))
        g.append(T(lx, y + 12, f'ESC PAD M{escpad[k]}', 10.5, anchor=anc, color=THIN, font=MONO, ls=0))
    # warnings, colours, params
    warn = ['⚠ VERIFY EVERY PAD LABEL AGAINST THE SpeedyBee F405 V4 MANUAL.',
            '   ArduPilot docs: UART2 = RC, UART4 = Bluetooth (not usable),',
            '   UART5 = ESC telemetry, UART6 = GPS.',
            '⚠ MOTOR TEST (MISSION PLANNER) BEFORE FITTING PROPS: CHECK ORDER',
            '   AND SPIN; SWAP ANY 2 PHASE WIRES TO REVERSE A MOTOR.',
            '⚠ FIRST POWER-UP THROUGH A SMOKE STOPPER.']
    for i, t in enumerate(warn):
        g.append(T(1080, 500 + i * 18, t, 11.5, anchor='start', color=ACC if t.startswith('⚠') else INK, ls=0))
    lx = 1080
    g.append(T(lx, 640, 'ARDUPILOT STARTING PARAMETERS', 13, anchor='start', weight='bold', color=ACC, ls=1.2))
    ptxt = ['FRAME_CLASS=1  FRAME_TYPE=1   (QUAD X)', 'SERVO1_FUNCTION=36  SERVO2_FUNCTION=33', 'SERVO3_FUNCTION=34  SERVO4_FUNCTION=35',
            '  ↳ ESC PADS M1–M4 → ARDUPILOT MOTORS', 'MOT_PWM_TYPE=6      (DSHOT600)', 'SERIAL2_PROTOCOL=23 (ELRS / CRSF RC)',
            'SERIAL6_PROTOCOL=5  (GPS)', 'SERIAL3_PROTOCOL=44 (IRC TRAMP VTX)', 'BATT_MONITOR=4      (ESC CURRENT + VBAT)']
    for i, t in enumerate(ptxt): g.append(T(lx, 660 + i * 17, t, 11, anchor='start', font=MONO, ls=0))
    cx2 = 1430
    g.append(T(cx2, 830, 'WIRE COLOURS', 13, anchor='start', weight='bold', color=ACC, ls=1.2)) if False else None
    g.append(T(lx, 830, 'WIRE COLOURS', 13, anchor='start', weight='bold', color=ACC, ls=1.2))
    cl = [(C_RED, '+ POWER'), (C_BLK, 'GROUND'), (C_YEL, 'SIGNAL OUT (TX / VIDEO)'), (C_GRN, 'SIGNAL IN (RX / CONTROL)'),
          (C_BLU, 'I²C SDA'), (C_VIO, 'I²C SCL'), (C_ORG, 'MOTOR PHASES (3 PER MOTOR)')]
    for i, (c, t) in enumerate(cl):
        x = lx + (i % 2) * 260; y = 852 + (i // 2) * 17
        g.append(L(x, y - 4, x + 26, y - 4, c, 3)); g.append(T(x + 34, y, t, 10.5, anchor='start'))
    return svg(g)

# ================================================================ SHEET 7: fit check
def sheet7():
    g = frame('FIT CHECK REPORT', 'K5-400', 7, 'NTS', 'REAL PART SIZES vs FRAME (CAD INTERFERENCE TEST)')
    comp_rows = [
        ('FLIGHT CONTROLLER', 'SpeedyBee F405 V4', '41.6 x 39.4 x 7.8', 'RETAILER SPECS'),
        ('ESC 4-IN-1', 'SpeedyBee BLS 55A', '45.6 x 44 x 8', 'RETAILER SPECS'),
        ('STACK HEIGHT', 'FC + ESC + GROMMETS', '18.3', 'MANUAL'),
        ('VTX', 'SpeedyBee TX800', '28 x 28 x 5.5*', 'PCB SPEC; *THK ASSUMED'),
        ('CAMERA', 'Caddx Ratel 2', '19 x 19 x 20', 'RETAILER SPECS'),
        ('MOTOR', 'iFlight XING2 2207', 'Ø29.08 x 19.1, 16x16 M3', 'RETAILER SPECS'),
        ('PROP', '5.1" TRI-BLADE', 'Ø129.5', 'NOMINAL'),
        ('BATTERY', 'Tattu R-Line V5 6S 1200', '78 x 40 x 34', 'RETAILER SPECS'),
        ('GPS', 'Matek M10Q-5883', '20 x 20 x 12.4', 'RETAILER SPECS'),
        ('RECEIVER', 'Radiomaster RP1 V2', '13 x 11 x 3', 'MANUFACTURER'),
        ('XT60 FEMALE', 'Amass XT60', '15.8 x 8.2 x 16', 'COMMON SIZE — VERIFY'),
    ]
    g.append(T(70, 90, 'COMPONENT SIZES USED', 16, anchor='start', weight='bold', ls=2))
    g += table(70, 100, [('COMPONENT', 190, 'start'), ('MODEL', 230, 'start'), ('SIZE (mm)', 200, 'start'), ('SOURCE', 190, 'start')], comp_rows, rh=22)
    res = [
        ('ESC ↔ CANOPY WALL', '1.0', 'PASS', 'BODY WIDENED 42 → 50 mm'),
        ('FC ↔ CANOPY WALL', '3.0', 'PASS', ''),
        ('VTX ↔ TOP PLATE', '2.7', 'PASS', 'VTX PLATE ON STACK (NEW)'),
        ('VTX PLATE ↔ FC', '2.4', 'PASS', 'SITS ON STACK NUTS'),
        ('CAMERA ↔ CRADLE WALLS', '0.2 / SIDE', 'SNUG', 'INTENDED FRICTION FIT'),
        ('CAMERA ↔ FC', '≥ 2', 'PASS', 'AT 30° TILT'),
        ('CAMERA ↔ CANOPY', '≥ 1', 'PASS', ''),
        ('MOTOR BELL ↔ ARM SPINE', '2.5', 'PASS', ''),
        ('PROP TIP ↔ CANOPY / BODY', '5.6', 'PASS', 'WHEELBASE 225 → 230, R10'),
        ('PROP ↔ ANTENNA MOUNT', '≥ 3', 'PASS', ''),
        ('PROP ↔ TOWER, GOPRO, PLATES', '≥ 5', 'PASS', ''),
        ('BATTERY ↔ GOPRO / TOWER', '1.25 EACH', 'PASS', 'BAY 76.5 → 80.5 mm'),
        ('BATTERY WIDTH ↔ STRAP SLOTS', '40 / 43 C-C', 'PASS', 'SLOTS MOVED OUT'),
        ('GPS ↔ POCKET', '0.3 / SIDE', 'SNUG', 'PLATFORM FLOOR FIXED'),
        ('XT60 ↔ POCKET', '0.25 / SIDE', 'SNUG', 'ZIP-TIE RETAINED'),
        ('MOTOR-WIRE EXIT ↔ CANOPY', 'OPEN', 'PASS', '4 CORNER EXITS (NEW)'),
        ('MOTOR SCREW LENGTH', 'M3 x 8', 'NOTE', 'SUPPLIED M3x6/7 TOO SHORT'),
        ('STACK BOLT LENGTH', '≥ 29.3', 'NOTE', 'USE M3 x 30–35'),
    ]
    g.append(T(70, 100 + 22 * 13 + 30, 'CLEARANCE RESULTS (mm)', 16, anchor='start', weight='bold', ls=2))
    y0 = 100 + 22 * 13 + 40
    g += table(70, y0, [('INTERFACE', 270, 'start'), ('MIN. GAP', 110, 'middle'), ('RESULT', 80, 'middle'), ('NOTE / CHANGE MADE', 350, 'start')], res, rh=21)
    side = ['METHOD', 'Each bought part was modelled at its published size and placed',
            'where it mounts. OpenSCAD intersected it with every frame part',
            'it could touch, then grew it by 0.5, 1, 2, 3 and 5 mm and re-',
            'tested. The gap is the largest growth with no overlap.', '',
            'ISSUES FOUND AND FIXED IN THIS REVISION', '1. ESC 45.6 mm DID NOT FIT THE 42 mm BODY → BODY 50 mm.',
            '2. BATTERY 78 mm DID NOT FIT THE 76.5 mm BAY → TOWER MOVED BACK.',
            '3. NO VTX MOUNTING → VTX PLATE ON THE STACK (ITEM 9).', '4. GPS PLATFORM STOOD 1 mm INTO THE POCKET → FIXED.',
            '5. MOTOR WIRES HAD NO EXIT THROUGH THE CANOPY → 4 EXITS.', '6. WHEELBASE 230 FOR 5.1" PROP-TIP MARGIN.', '',
            'LIMITS', '• SIZES ARE FROM RETAILER LISTINGS; MEASURE YOUR PARTS.',
            '• VTX THICKNESS AND XT60 LENGTH ARE ASSUMED.', '• WIRES, SOLDER JOINTS AND CONNECTORS ARE NOT MODELLED.',
            '• PRINT TOLERANCE IS NOT INCLUDED — PRINT THE TEST COUPON.']
    for i, t in enumerate(side):
        hdr = t in ('METHOD', 'ISSUES FOUND AND FIXED IN THIS REVISION', 'LIMITS')
        g.append(T(1000, 110 + i * 19, t, 13 if hdr else 12, anchor='start', weight='bold' if hdr else 'normal', color=ACC if hdr else INK, ls=0.3))
    return svg(g)

SHEETS = [sheet1, sheet2, sheet3, sheet4, sheet5, sheet6, sheet7]
if __name__ == '__main__':
    for i, f in enumerate(SHEETS, 1):
        open(os.path.join(OUT, f'K5_sheet{i}.svg'), 'w').write(f())
    print('wrote', len(SHEETS), 'sheets')
