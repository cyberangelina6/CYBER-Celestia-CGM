"""Draw the side-view outlines used by the Fusion script, without Fusion.

    pip install matplotlib
    python Fusion/preview/preview_side.py

Writes Fusion/preview/side-view.png. Handy for checking proportions after
editing the DIMENSIONS block, before re-running the script in Fusion.
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
SCRIPT = os.path.join(HERE, '..', 'Scripts', 'CelestiaGunMouse', 'CelestiaGunMouse.py')

# Stub out the Fusion API so the geometry part of the script can be imported.
adsk = types.ModuleType('adsk')
adsk.core = types.SimpleNamespace()
adsk.fusion = types.SimpleNamespace(FeatureOperations=types.SimpleNamespace(
    NewBodyFeatureOperation=0, JoinFeatureOperation=1, CutFeatureOperation=2))
sys.modules.update({'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion})
spec = importlib.util.spec_from_file_location('cgm', SCRIPT)
cgm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cgm)


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


def loop_path(loop):
    if loop[0][0] == 'circle':
        (cx, cy), r = loop[0][1], loop[0][2]
        pts = [(cx + r * math.cos(t * math.pi / 32), cy + r * math.sin(t * math.pi / 32)) for t in range(65)]
    else:
        pts = []
        for seg in loop:
            seg_pts = [seg[1], seg[2]] if seg[0] == 'line' else arc_points(*seg[1:])
            pts.extend(seg_pts if not pts else seg_pts[1:])
    return Path(pts, [Path.MOVETO] + [Path.LINETO] * (len(pts) - 1))


def _signed_area(v):
    return sum(v[i][0] * v[i - 1][1] - v[i - 1][0] * v[i][1] for i in range(len(v))) / 2


def compound(loops):
    """First loop is the outline; any further loops are holes."""
    paths = []
    for i, lp in enumerate(loops):
        v = loop_path(lp).vertices
        if (_signed_area(v) > 0) == (i > 0):     # outline CW, holes CCW
            v = v[::-1]
        paths.append(Path(v, [Path.MOVETO] + [Path.LINETO] * (len(v) - 1)))
    return Path.make_compound_path(*paths)


def draw(ax, loops, rgb, z, edge='#5b1d5e', alpha=1.0):
    color = tuple(c / 255 for c in rgb)
    ax.add_patch(PathPatch(compound(loops), facecolor=color, edgecolor=edge, lw=1.4,
                           alpha=alpha, zorder=z))


fig, ax = plt.subplots(figsize=(12, 8))
C = cgm.COLORS
x0, x1, x2 = cgm.muzzle_x_positions()
y = cgm.BORE_AXIS_Y

# Back to front, roughly how the parts overlap from the left side.
if cgm.INCLUDE_GRIP_LOOP:
    draw(ax, [cgm.grip_loop_outline()], C['Rear Cap (Heart)'], 1)
draw(ax, [cgm.grip_outline()], C['Frame & Grip'], 2)
draw(ax, cgm.guard_loops(), C['Frame & Grip'], 3)
draw(ax, [cgm.trigger_outline()], C['Trigger'], 3.5)
ring, tab = cgm.eyelet_loops()
draw(ax, [tab], C['Frame & Grip'], 3)
draw(ax, ring, C['Frame & Grip'], 3)
draw(ax, [cgm.frame_outline()], C['Frame & Grip'], 4)
draw(ax, [cgm.readout_outline()], (120, 40, 110), 4.5)
draw(ax, [cgm.cap_outline()], C['Rear Cap (Heart)'], 5)
draw(ax, [cgm.slide_outline()], C['Slide'], 6)
for s in cgm.serration_outlines():
    draw(ax, [s], (170, 40, 120), 6.5)
draw(ax, [cgm.rear_sight_outline()], C['Slide'], 5.5)
draw(ax, [cgm.button_outline()], C['Top Button'], 5.5)
muz = [cgm.polygon([(x0, y - cgm.SHROUD_R), (x1, y - cgm.SHROUD_R), (x1, y + cgm.SHROUD_R), (x0, y + cgm.SHROUD_R)]),
       cgm.polygon([(x1, y - cgm.MUZZLE_R), (x2, y - cgm.MUZZLE_R), (x2, y + cgm.MUZZLE_R), (x1, y + cgm.MUZZLE_R)])]
draw(ax, muz[:1], C['Muzzle & Shroud'], 7)
draw(ax, muz[1:], C['Muzzle & Shroud'], 7)
draw(ax, cgm.front_sight_loops(), C['Muzzle & Shroud'], 6.8)
draw(ax, cgm.charm_loops(), C['Charm'], 7)
ax.plot([cgm.EYELET_CENTER[0], cgm.CHARM_CENTER[0]],
        [cgm.EYELET_CENTER[1] - cgm.EYELET_R_IN, cgm.CHARM_CENTER[1] + 4.5],
        ls=':', lw=2.5, color='#b04a9a', zorder=0)

labels = {
    'slide': (60, 15), 'muzzle': (x2 - 9, y), 'front sight': (x2 - 8, 44),
    'rear cap': (-20, 22), 'grip loop': (-36, -24), 'grip': (8, -60),
    'trigger': (70, -28), 'readout': (88, -8), 'charm': (cgm.CHARM_CENTER[0], -74),
    'top button': (40, 39),
}
for text, (lx, ly) in labels.items():
    ax.annotate(text, (lx, ly), ha='center', va='center', fontsize=9, color='#3b0f3d',
                zorder=20, bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.75))

ax.set_aspect('equal')
ax.set_xlim(-45, 170)
ax.set_ylim(-110, 50)
ax.invert_xaxis()      # muzzle on the left, like the sketch
ax.grid(True, color='#eee', zorder=-1)
ax.set_xlabel('x (mm, toward muzzle)')
ax.set_ylabel('y (mm)')
ax.set_title('CYBER Celestia CGM - left side view (outlines from the Fusion script)')
out = os.path.join(HERE, 'side-view.png')
fig.savefig(out, dpi=110, bbox_inches='tight')
print('wrote', out)
