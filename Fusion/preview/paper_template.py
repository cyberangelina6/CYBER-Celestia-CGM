"""Full-size (1:1) paper template of the gun's left side, to check hand fit
before paying for a print.

    pip install matplotlib
    python Fusion/preview/paper_template.py

Writes Fusion/preview/paper-template-1to1.pdf (US Letter, landscape).
Print it at "Actual size" / 100% (NOT "Fit to page"), then check the 50 mm
scale bar with a ruler before cutting it out.
"""
import importlib.util
import os
import sys
import types

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, '..', 'Scripts', 'CelestiaGunMouse', 'CelestiaGunMouse.py')

adsk = types.ModuleType('adsk')
adsk.core = types.SimpleNamespace()
adsk.fusion = types.SimpleNamespace(FeatureOperations=types.SimpleNamespace(
    NewBodyFeatureOperation=0, JoinFeatureOperation=1, CutFeatureOperation=2))
sys.modules.update({'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion})
spec = importlib.util.spec_from_file_location('cgm', SCRIPT)
cgm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cgm)

# Reuse the preview's curve helpers (loading it also refreshes side-view.png)
pspec = importlib.util.spec_from_file_location('preview', os.path.join(HERE, 'preview_side.py'))
pv = importlib.util.module_from_spec(pspec)
pspec.loader.exec_module(pv)

PAGE_W, PAGE_H = 279.4, 215.9            # US Letter landscape, mm
fig = plt.figure(figsize=(PAGE_W / 25.4, PAGE_H / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
# x runs toward the muzzle; flip so the muzzle points left, like the sketch
x_mid, y_mid = (cgm.MUZZLE_X1 - 36.0) / 2.0, -14.0
ax.set_xlim(x_mid + PAGE_W / 2, x_mid - PAGE_W / 2)
ax.set_ylim(y_mid - PAGE_H / 2, y_mid + PAGE_H / 2)
ax.set_aspect('equal')
ax.axis('off')


def outline(loops, lw=1.0, ls='-', fill='none'):
    ax.add_patch(PathPatch(pv.compound(loops), facecolor=fill, edgecolor='black', lw=lw, ls=ls))


y, r = cgm.BORE_AXIS_Y, cgm.BARREL_R
outline([pv.rect(cgm.BARREL_X0, y - r, cgm.FLANGE_X, y + r)])
outline([pv.rect(cgm.FLANGE_X, y - cgm.MUZZLE_R, cgm.MUZZLE_X1, y + cgm.MUZZLE_R)])
fl = cgm.heart_shape(cgm.FLANGE_HEART_W)[1]
outline([pv.rect(cgm.FLANGE_X, cgm.FLANGE_HEART_CY - fl['h'], cgm.FLANGE_X + cgm.FLANGE_T,
                 cgm.FLANGE_HEART_CY + fl['r'])])
outline([cgm.slide_outline()], lw=1.4)
outline([cgm.ears_outline()])
outline([cgm.button_outline()])
outline([cgm.frame_outline()], lw=1.4)
outline([cgm.readout_outline()], ls='--')
outline([cgm.cap_outline()], lw=1.4)
outline([cgm.grip_loop_outline()])
grip_pts = pv.grip_side_silhouette()
outline([cgm.polygon(grip_pts)], lw=1.4)
outline(cgm.guard_loops())
for loop in cgm.trigger_loops()[2:3] + cgm.ads_loops()[2:3]:
    outline([loop])
for pos in (cgm.INFUSE_POS, cgm.RECENTER_POS):
    outline([[('circle', pos, cgm.SIDE_BUTTON_D / 2)]])

# 50 mm scale bar to check the print came out at 100%
sx, sy = x_mid + PAGE_W / 2 - 15, y_mid - PAGE_H / 2 + 12
ax.plot([sx, sx - 50], [sy, sy], color='black', lw=2)
for xx in (sx, sx - 50):
    ax.plot([xx, xx], [sy - 2, sy + 2], color='black', lw=2)
ax.text(sx - 25, sy + 3, '50 mm - check with a ruler', ha='center', va='bottom', fontsize=8)
ax.text(x_mid, y_mid + PAGE_H / 2 - 8,
        'CYBER Celestia CGM, left side, 1:1. Print at Actual size / 100%, cut out, hold like the gun.',
        ha='center', va='top', fontsize=8)

out = os.path.join(HERE, 'paper-template-1to1.pdf')
fig.savefig(out)
print('wrote', out)
