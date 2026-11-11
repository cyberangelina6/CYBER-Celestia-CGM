"""Draw the outlines used by the Fusion script, without Fusion.

    pip install matplotlib pillow
    python Fusion/preview/preview_side.py

Writes Fusion/preview/side-view.png: the left side view, a front view of the
muzzle/shroud, and the concept sketch for comparison. Handy for checking
proportions after editing the DIMENSIONS block, before re-running in Fusion.
"""
import importlib.util
import math
import os
import sys
import types

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
SCRIPT = os.path.join(HERE, '..', 'Scripts', 'CelestiaGunMouse', 'CelestiaGunMouse.py')
SKETCH = os.path.join(ROOT, 'reference', 'concept-sketch-v1.webp')

# Stub out the Fusion API so the geometry part of the script can be imported.
adsk = types.ModuleType('adsk')
adsk.core = types.SimpleNamespace()
adsk.fusion = types.SimpleNamespace(FeatureOperations=types.SimpleNamespace(
    NewBodyFeatureOperation=0, JoinFeatureOperation=1, CutFeatureOperation=2))
sys.modules.update({'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion})
spec = importlib.util.spec_from_file_location('cgm', SCRIPT)
cgm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cgm)
C = cgm.BODY_COLORS
P = {n: v for n, v, _ in cgm.LIVE_PARAMS}


def arc_points(p0, pm, p1, n=24):
    c, r = cgm.circle_through(p0, pm, p1)
    a0, am, a1 = (math.atan2(p[1] - c[1], p[0] - c[0]) for p in (p0, pm, p1))

    def norm(a):
        return (a - a0) % (2 * math.pi)
    sweep = norm(a1)
    if norm(am) > sweep:          # mid point not on the CCW path -> go clockwise
        sweep -= 2 * math.pi
    return [(c[0] + r * math.cos(a0 + sweep * i / n), c[1] + r * math.sin(a0 + sweep * i / n))
            for i in range(n + 1)]


def spline_points(pts, n=12):
    """Catmull-Rom curve through the points (close to Fusion's fitted spline)."""
    ext = [pts[0]] + list(pts) + [pts[-1]]
    out = [pts[0]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(1, n + 1):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    return out


def loop_vertices(loop):
    if loop[0][0] == 'circle':
        (cx, cy), r = loop[0][1], loop[0][2]
        return [(cx + r * math.cos(t * math.pi / 32), cy + r * math.sin(t * math.pi / 32)) for t in range(65)]
    pts = []
    for seg in loop:
        if seg[0] == 'line':
            seg_pts = [seg[1], seg[2]]
        elif seg[0] == 'arc':
            seg_pts = arc_points(*seg[1:])
        else:
            seg_pts = spline_points(seg[1:])
        pts.extend(seg_pts if not pts else seg_pts[1:])
    return pts


def _signed_area(v):
    return sum(v[i][0] * v[i - 1][1] - v[i - 1][0] * v[i][1] for i in range(len(v))) / 2


def compound(loops):
    """First loop is the outline; any further loops are holes."""
    paths = []
    for i, lp in enumerate(loops):
        v = loop_vertices(lp)
        if (_signed_area(v) > 0) == (i > 0):     # outline CW, holes CCW
            v = v[::-1]
        paths.append(Path(v, [Path.MOVETO] + [Path.LINETO] * (len(v) - 1)))
    return Path.make_compound_path(*paths)


def draw(ax, loops, rgb, z, edge='#5b1d5e'):
    ax.add_patch(PathPatch(compound(loops), facecolor=tuple(c / 255 for c in rgb),
                           edgecolor=edge, lw=1.3, zorder=z))


def rect(x0, y0, x1, y1):
    return cgm.polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


fig = plt.figure(figsize=(16, 9))
ax = fig.add_axes([0.03, 0.06, 0.62, 0.88])
axf = fig.add_axes([0.655, 0.36, 0.17, 0.60])
axg = fig.add_axes([0.835, 0.62, 0.16, 0.28])
axs = fig.add_axes([0.835, 0.04, 0.16, 0.50])

# ---- Left side view (back to front, roughly how parts overlap) ----
y, r = cgm.BORE_AXIS_Y, cgm.BARREL_R
if cgm.INCLUDE_GRIP_LOOP:
    draw(ax, [cgm.grip_loop_outline()], C['Frame & Grip'], 1)
draw(ax, cgm.guard_loops(), C['Grip panel'], 3.05, edge='none')
def grip_side_silhouette():
    """Grip outline above GRIP_CUT_Y plus the blend down to the oval base."""
    v = loop_vertices(cgm.grip_outline())
    cut = cgm.GRIP_CUT_Y
    above = []
    hits = []
    for i in range(len(v)):
        p, q = v[i - 1], v[i]
        if (p[1] - cut) * (q[1] - cut) < 0:
            t = (cut - p[1]) / (q[1] - p[1])
            hits.append((p[0] + t * (q[0] - p[0]), cut))
            above.append(hits[-1])
        if q[1] >= cut:
            above.append(q)
    xf, xb = max(h[0] for h in hits), min(h[0] for h in hits)
    bf = cgm.BASE_CENTER_X + cgm.BASE_LENGTH / 2
    bb = cgm.BASE_CENTER_X - cgm.BASE_LENGTH / 2
    # replace the straight cut with the blend: front corner -> base -> back corner
    i = above.index((xf, cut))
    j = above.index((xb, cut))
    if i < j:
        return above[:i + 1] + [(bf, cgm.GRIP_BASE_Y), (bb, cgm.GRIP_BASE_Y)] + above[j:]
    return above[:j + 1] + [(bb, cgm.GRIP_BASE_Y), (bf, cgm.GRIP_BASE_Y)] + above[i:]


grip_poly = Path(grip_side_silhouette() + [grip_side_silhouette()[0]])
ax.add_patch(PathPatch(grip_poly, facecolor=tuple(c / 255 for c in C['Frame & Grip']), edgecolor='none', zorder=3))
seam_pts = loop_vertices(cgm.grip_seam())
front_of_seam = Path(seam_pts + [(seam_pts[-1][0], -150), (250, -150), (250, seam_pts[0][1]), seam_pts[0]])
panel = PathPatch(grip_poly, facecolor=tuple(c / 255 for c in C['Grip panel']), edgecolor='none', zorder=3.1)
ax.add_patch(panel)
panel.set_clip_path(PathPatch(front_of_seam, transform=ax.transData))
seam_line, = ax.plot([p[0] for p in seam_pts], [p[1] for p in seam_pts], color='#5b1d5e', lw=1.0, zorder=3.15)
seam_line.set_clip_path(PathPatch(grip_poly, transform=ax.transData))
ax.add_patch(PathPatch(grip_poly, fill=False, edgecolor='#5b1d5e', lw=1.3, zorder=3.2))
draw(ax, [[('circle', cgm.GRIP_PIN, cgm.GRIP_PIN_R)]], C['Grip pin'], 3.2)
for loop in cgm.trigger_loops():
    draw(ax, [loop], C['Trigger'], 3.6, edge='none')
for loop in cgm.ads_loops():
    draw(ax, [loop], C['ADS lever'], 3.6, edge='none')
for (x0, x1, y0, y1) in (cgm.TRIGGER_SWITCH, cgm.ADS_SWITCH):
    draw(ax, [rect(x0, y0, x1, y1)], C['Switch (reference)'], 3.7)
for pivot in (cgm.TRIGGER_PIVOT, cgm.ADS_PIVOT):
    draw(ax, [[('circle', pivot, cgm.PIVOT_PIN_R)]], (255, 255, 255), 3.8)
for host, posts in cgm.SCREW_POSTS.items():
    for pos in posts:
        draw(ax, [[('circle', pos, cgm.POST_R)], [('circle', pos, cgm.SCREW_CLEAR_R)]], (180, 180, 190), 7.5)
ring, tab = cgm.eyelet_loops()
draw(ax, [tab], C['Frame & Grip'], 3)
draw(ax, ring, C['Frame & Grip'], 3)
draw(ax, [cgm.frame_outline()], C['Frame & Grip'], 4)
draw(ax, [cgm.readout_outline()], (120, 40, 110), 4.5)
ax.text((cgm.READOUT_X0 + cgm.READOUT_X1) / 2, (cgm.READOUT_Y0 + cgm.READOUT_Y1) / 2, '0001',
        color='#f7a8d8', ha='center', va='center', fontsize=10, family='monospace', zorder=4.6)
draw(ax, [rect(cgm.BARREL_X0, y - r, cgm.FLANGE_X, y + r)], C['Barrel'], 4.8)
draw(ax, [rect(cgm.FLANGE_X, y - cgm.MUZZLE_R, cgm.MUZZLE_X1, y + cgm.MUZZLE_R)], C['Barrel'], 4.9)
draw(ax, [rect(cgm.MUZZLE_X1 - 2, y - cgm.MUZZLE_R - 0.5, cgm.MUZZLE_X1 + 1.5, y + cgm.MUZZLE_R + 0.5)],
     C['Muzzle lip'], 5)
fl = cgm.heart_shape(cgm.FLANGE_HEART_W)[1]
f_top = cgm.FLANGE_HEART_CY + fl['r']
f_bot = cgm.FLANGE_HEART_CY - fl['h']
draw(ax, [rect(cgm.FLANGE_X, f_bot, cgm.FLANGE_X + cgm.FLANGE_T, f_top)], C['Heart flange'], 5.2)
_, sight_c = cgm._sight_centre()
sight_top = sight_c[1] + cgm.SIGHT_R_OUT * math.cos(math.radians(cgm.SIGHT_GAP_DEG))
draw(ax, [rect(cgm.FLANGE_X + 1.5, sight_c[1] - cgm.SIGHT_R_OUT, cgm.FLANGE_X + 4.5, sight_top)],
     C['Heart flange'], 5.1)
draw(ax, [cgm.cap_outline()], C['Heart cap'], 5)
# Cream centre: roughly where the inner dome bulges out of the cap
cream = cgm.transform(cgm.cap_inset_outline(), 0.0, (0.0, 0.0), 1.0)
pc = cgm.heart_dome_centre(cgm.CAP_HEART_W, cgm.CAP_CENTER, cgm.CAP_TILT_DEG)
cream = [(seg[0],) + tuple((pc[0] + 0.72 * (q[0] - pc[0]), pc[1] + 0.72 * (q[1] - pc[1])) for q in seg[1:])
         for seg in cream]
draw(ax, [cream], C['Heart inset'], 5.1)
draw(ax, [cgm.ears_outline()], C['Frame & Grip'], 5.5)
draw(ax, [cgm.button_outline()], C['Reload button'], 5.5)
x0, x1 = cgm.LED_WINDOW_X
draw(ax, [rect(x0, cgm.SLIDE_H - cgm.TOP_STRIP_H, x1, cgm.SLIDE_H)], C['LED window'], 6.7)
ax.text((x0 + x1) / 2, cgm.SLIDE_H + 3.5, 'LED window', ha='center', fontsize=8, color='#3b0f3d', zorder=20)
for pos, key, lab in ((cgm.INFUSE_POS, 'Infuse button', 'infuse'), (cgm.RECENTER_POS, 'Recenter button', 'recenter')):
    draw(ax, [[('circle', pos, cgm.SIDE_BUTTON_D / 2)]], C[key], 7)
    ax.text(pos[0], pos[1] - cgm.SIDE_BUTTON_D / 2 - 3, lab, ha='center', va='top', fontsize=8,
            color='#3b0f3d', zorder=20, bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.8))
ax.add_patch(PathPatch(compound([cgm.stadium(cgm.BOARD_CENTER[0], cgm.BOARD_CENTER[1], *cgm.USB_HOLE)]),
                       fill=False, edgecolor='#5b1d5e', lw=1.0, ls='--', zorder=7))
ax.text(cgm.BOARD_CENTER[0] - 7, cgm.BOARD_CENTER[1], 'USB-C\n(right side)', ha='right', va='center',
        fontsize=7, color='#3b0f3d', zorder=20)
draw(ax, [cgm.slide_outline()], C['Slide'], 6)
for s in cgm.serration_outlines():
    draw(ax, [s], (170, 40, 120), 6.5)
draw(ax, [cgm.top_strip_outline()], C['Frame & Grip'], 6.6)
draw(ax, cgm.charm_loops(), C['Charm'], 7)
draw(ax, cgm.charm_bail_loops(), C['Charm'], 7)
bail = cgm.charm_bail_loops()[0][0]
ax.plot([cgm.EYELET_CENTER[0], bail[1][0]], [cgm.EYELET_CENTER[1] - cgm.EYELET_R_IN, bail[1][1] + 1.3],
        ls=':', lw=2.5, color='#b04a9a', zorder=0)

labels = {
    'slide': (100, 16), 'barrel': (150, y), 'shroud': (cgm.FLANGE_X + 3, f_bot - 4),
    'front sight': (cgm.FLANGE_X + 3, sight_top + 5), 'rear cap': (-8, 30),
    'grip loop': (-30, -28), 'grip': (15, -45), 'trigger': (52, -25), 'ADS': (44, -38), 'readout': (103, -18),
    'charm': (cgm.CHARM_CENTER[0], cgm.CHARM_CENTER[1] - 15), 'reload': (47, 44),
    'ears': (32, 47),
}
for text, (lx, ly) in labels.items():
    ax.annotate(text, (lx, ly), ha='center', va='center', fontsize=9, color='#3b0f3d', zorder=20,
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.8))
ax.set_aspect('equal')
ax.set_xlim(-45, 195)
ax.set_ylim(-80, 55)
ax.invert_xaxis()      # muzzle on the left, like the sketch
ax.grid(True, color='#eee', zorder=-1)
ax.set_title('Left side (mm)')

# ---- Front view of the muzzle / shroud ----
# whole gun seen from the front, back to front
gw = P['grip_width'] / 2
draw(axf, [cgm.polygon([(-gw, -cgm.FRAME_H + 1), (gw, -cgm.FRAME_H + 1), (gw, cgm.GRIP_CUT_Y),
                        (cgm.BASE_WIDTH / 2, cgm.GRIP_BASE_Y), (-cgm.BASE_WIDTH / 2, cgm.GRIP_BASE_Y),
                        (-gw, cgm.GRIP_CUT_Y)])], C['Grip panel'], 0.5)
draw(axf, [cgm.slide_section()], C['Slide'], 0.8)
draw(axf, [cgm.polygon([(-cgm.slide_half_width(cgm.SLIDE_H - cgm.TOP_STRIP_H), cgm.SLIDE_H - cgm.TOP_STRIP_H),
                        (cgm.slide_half_width(cgm.SLIDE_H - cgm.TOP_STRIP_H), cgm.SLIDE_H - cgm.TOP_STRIP_H),
                        (cgm.slide_half_width(cgm.SLIDE_H), cgm.SLIDE_H),
                        (-cgm.slide_half_width(cgm.SLIDE_H), cgm.SLIDE_H)])], C['Frame & Grip'], 0.85)
frame_front = rect(-cgm.FRAME_W / 2, -cgm.FRAME_H, cgm.FRAME_W / 2, 0.0)
draw(axf, [frame_front], C['Frame & Grip'], 0.9)
draw(axf, [rect(-cgm.SLIDE_BOTTOM_W / 2 - 15, 0.0, cgm.SLIDE_BOTTOM_W / 2 + 15, 1.6)], (255, 255, 255), 0.95,
     edge='none')   # hide the strip of the frame shape that sits above y = 0
draw(axf, [cgm.slide_section()], C['Slide'], 0.96)
draw(axf, cgm.flange_loops(), C['Heart flange'], 1)
draw(axf, cgm.flange_inset_loops(), C['Heart inset'], 2)
draw(axf, cgm.front_sight_loops(), C['Heart flange'], 1.5)
draw(axf, cgm.sight_bead_loops(), C['Sight bead'], 1.6)
draw(axf, [[('circle', (0, y), cgm.MUZZLE_R + 0.5)], [('circle', (0, y), cgm.MUZZLE_LIP_R_IN)]], C['Muzzle lip'], 3)
draw(axf, [[('circle', (0, y), cgm.MUZZLE_LIP_R_IN)], [('circle', (0, y), cgm.BORE_R)]], C['Heart flange'], 3)
draw(axf, [[('circle', (0, y), cgm.BORE_R)]], (200, 70, 160), 3)
axf.set_aspect('equal')
axf.set_xlim(-40, 40)
axf.set_ylim(cgm.GRIP_BASE_Y - 4, 54)
axf.grid(True, color='#eee', zorder=-1)
axf.set_title('From the front')

# ---- Bottom of the grip (gun flipped over): a flat oval ----
cx, L, W = cgm.BASE_CENTER_X, cgm.BASE_LENGTH, cgm.BASE_WIDTH
oval = [(cx + L / 2 * math.cos(t * math.pi / 40), W / 2 * math.sin(t * math.pi / 40)) for t in range(81)]
oval_path = Path(oval)
axg.add_patch(PathPatch(oval_path, facecolor=tuple(c / 255 for c in C['Frame & Grip']), edgecolor='none', zorder=1))
seam_x = cgm.spine_front_x(cgm.GRIP_BASE_Y)
dark = PathPatch(oval_path, facecolor=tuple(c / 255 for c in C['Grip panel']), edgecolor='none', zorder=2)
axg.add_patch(dark)
dark.set_clip_path(PathPatch(Path([(seam_x, -50), (200, -50), (200, 50), (seam_x, 50), (seam_x, -50)]),
                             transform=axg.transData))
axg.plot([seam_x, seam_x], [-W / 2, W / 2], color='#5b1d5e', lw=0.8, zorder=2.5)
axg.add_patch(PathPatch(oval_path, fill=False, edgecolor='#5b1d5e', lw=1.3, zorder=3))
axg.text(cx + L / 2 - 4, 0, 'front', rotation=90, ha='center', va='center', fontsize=8, color='#3b0f3d', zorder=4)
axg.set_aspect('equal')
axg.set_xlim(cx - L / 2 - 6, cx + L / 2 + 6)
axg.set_ylim(-W / 2 - 6, W / 2 + 6)
axg.invert_xaxis()
axg.grid(True, color='#eee', zorder=-1)
axg.set_title('Bottom (flipped over)')

# ---- The concept sketch ----
try:
    from PIL import Image
    axs.imshow(Image.open(SKETCH))
    axs.set_title('Concept sketch v1')
except Exception as exc:          # Pillow missing or file moved
    axs.text(0.5, 0.5, 'sketch not shown:\n{}'.format(exc), ha='center', va='center')
axs.axis('off')

out = os.path.join(HERE, 'side-view.png')
fig.savefig(out, dpi=110, bbox_inches='tight')
print('wrote', out)
