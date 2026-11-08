"""
CYBER Celestia - Custom Gun Mouse (CGM)
Starter model for Autodesk Fusion, built from concept sketch v1
(reference/concept-sketch-v1.webp).

HOW TO RUN
  Utilities > Add-Ins > Scripts and Add-Ins > "+" (Script or add-in from
  device) > pick this folder > select CelestiaGunMouse > Run.
  The script always opens a NEW design, so it never touches your other work.

WHAT YOU GET (one component per part of the sketch)
  Slide (cat-ear rear sight, grooves), Muzzle & Shroud (barrel, heart flange,
  front sight ring, muzzle rings), Frame & Grip (frame, readout window,
  trigger guard, two-tone grip, charm eyelet), Trigger, Top Button,
  Rear Cap (puffy 3D heart + grip loop) and Charm (heart padlock).

EDITING
  * Thicknesses (side-to-side widths, cut depths) are live Fusion parameters:
    Modify > Change Parameters. Change them and the model updates.
  * Outlines (lengths, heights, angles, positions) are the numbers in the
    DIMENSIONS block below. Edit them and run the script again.
    Fusion/preview/preview_side.py draws them without Fusion.

COORDINATES USED IN THIS FILE (millimetres)
  x grows toward the muzzle, y grows up, y = 0 is where the slide sits on
  the frame, and x = 0 is the bottom-rear corner of the slide.
  In Fusion the gun is mirrored so the muzzle points to -X and the LEFT side
  (the side in the sketch, with the readout) faces you in the Front view.
"""

import math
import traceback

import adsk.core
import adsk.fusion


# =============================================================================
# DIMENSIONS (mm). Edit these, then re-run the script.
# =============================================================================

# Slide: a parallelogram whose front and rear ends lean forward at the top
SLIDE_LEN = 134.0           # along the bottom edge
SLIDE_H = 32.0
SLIDE_FRONT_LEAN = 10.0     # top of the front face sits this far forward
SLIDE_FRONT_BEVEL = 6.0     # bevel on the top-front corner
SLIDE_REAR_LEAN = 24.0      # top of the rear face sits this far forward
SERRATION_XS = (56.0, 63.0, 70.0, 82.0)   # where each groove starts (bottom)
SERRATION_W = 1.6           # groove width
SERRATION_LEAN = 11.0       # how far forward the top of each groove leans

# Rear sight: two cat ears on top of the slide, just in front of the heart
EARS_X0 = 26.0              # rear edge of the ears
EARS_LEN = 12.0
EARS_H = 10.0
EARS_GAP = 6.0              # gap between the two ears

# Top button (pill on top of the slide)
BUTTON_X0, BUTTON_X1 = 40.0, 54.0
BUTTON_H = 5.0

# Barrel and muzzle (revolved around a horizontal axis)
BORE_AXIS_Y = 11.0          # height of the barrel centreline
BARREL_R = 15.0
BARREL_X0 = 128.0           # starts inside the slide
FLANGE_X = 162.0            # rear face of the heart flange (the "shroud")
FLANGE_T = 6.0              # flange thickness
MUZZLE_X1 = 184.0           # front face of the muzzle
MUZZLE_LIP_R_IN = 11.0      # cream lip ring on the muzzle front
MUZZLE_RING_R = 9.5         # inner ring step
BORE_R = 7.0
BORE_DEPTH = 15.0

# Heart flange (shroud) around the barrel, tip pointing down
FLANGE_HEART_W = 52.0
FLANGE_HEART_CY = 16.0      # height of the line between the two lobes

# Front sight: ring facing forward, sitting in the flange heart's top dip
SIGHT_R_OUT = 6.0
SIGHT_R_IN = 3.5
SIGHT_LIFT = 5.0            # ring centre height above the heart's dip

# Frame (strip under the slide)
FRAME_REAR_X = 4.0
FRAME_FRONT_X = 128.0
FRAME_H = 12.0

# Readout window (recess on the left side for a small display)
READOUT_X0, READOUT_X1 = 84.0, 122.0
READOUT_Y0, READOUT_Y1 = -10.0, -2.0

# Grip: one shape, split into a light-pink back piece and a darker front
# panel that sit flush and share one flat, rounded base.
SPINE_REAR_TOP_X = 1.0      # back of the grip where it meets y = 0
SPINE_REAR_RAKE = 28.0      # degrees from vertical
SPINE_FRONT_TOP_X = 14.0    # colour seam (light/dark) at the frame bottom
SPINE_FRONT_RAKE = 24.0
# Front edge of the panel: a smooth curve through these points, top to bottom
PANEL_FRONT = [(36.0, -10.0), (36.5, -22.0), (31.5, -40.0), (33.0, -54.0), (32.0, -63.0)]
# Flat oval base: below GRIP_CUT_Y the grip blends smoothly into a flat,
# level bottom that is an ellipse when you flip the gun over.
GRIP_CUT_Y = -50.0              # where the blend into the base starts
GRIP_BASE_Y = -72.0             # the flat bottom
BASE_CENTER_X = -2.0            # centre of the oval (front/back)
BASE_LENGTH = 62.0              # oval length, front to back
BASE_WIDTH = 34.0               # oval width, side to side
GRIP_PIN = (19.0, -16.0)        # the little pin/screw at the top of the grip
GRIP_PIN_R = 2.2

# Trigger guard (compact loop in front of the grip)
GUARD_OUT_FRONT_X = 70.0
GUARD_OUT_BOTTOM_Y = -36.0
GUARD_IN_REAR_X = 38.0
GUARD_IN_FRONT_X = 66.0
GUARD_IN_BOTTOM_Y = -32.0

# Heart rear cap: a puffy 3D heart (doubles as a palm rest)
CAP_CENTER = (-8.0, 18.0)   # midway between the two lobe centres
CAP_HEART_W = 58.0          # lobe-to-lobe width before tilting
CAP_TILT_DEG = 40.0         # tilts the tip forward/down into the slide
CAP_DEPTH = 30.0            # thickness at the fullest part of the lobes
CAP_INSET_SCALE = 0.85      # size of the cream heart inside the cap
CAP_INSET_PROUD = 2.0       # how far the cream centre bulges out of each side
INSET_SCALE = 0.68          # cream inner heart size on the flange

# Grip loop: tapered band from the heart down into the grip back piece
INCLUDE_GRIP_LOOP = True
LOOP_START = (-22.0, -1.0)  # inside the heart's rear lobe
LOOP_MID = (-21.0, -19.0)
LOOP_END = (-14.0, -37.0)   # inside the grip back piece
LOOP_T_START, LOOP_T_END = 7.0, 4.0

# Charm (heart padlock) hanging from an eyelet at the front of the frame
EYELET_CENTER = (120.0, -15.0)
EYELET_R_OUT, EYELET_R_IN = 3.2, 1.6
CHARM_CENTER = (123.0, -46.0)
CHARM_W = 19.0

# Fillet radii (if a fillet fails, the script skips it and tells you)
FILLET_SLIDE = 2.0
FILLET_FRAME = 1.5
FILLET_GRIP = 8.0               # big, so the grip and base are round
FILLET_GUARD = 2.0
FILLET_SMALL = 1.0

# Live parameters: (name, value in mm, comment). Shown in Change Parameters.
LIVE_PARAMS = [
    ('slide_width', 28.0, 'Slide thickness, side to side'),
    ('frame_width', 22.0, 'Frame thickness, side to side'),
    ('grip_width', 30.0, 'Grip panel (dark pink) thickness, side to side'),
    ('guard_width', 12.0, 'Trigger guard thickness'),
    ('trigger_width', 7.0, 'Trigger blade thickness'),
    ('button_width', 9.0, 'Top button width'),
    ('flange_width', 6.0, 'Heart flange (shroud) thickness'),
    ('inset_proud', 1.5, 'How far the cream heart insets stand out'),
    ('loop_width', 10.0, 'Grip loop thickness'),
    ('sight_thickness', 3.0, 'Front sight ring thickness'),
    ('charm_thickness', 4.0, 'Heart charm thickness'),
    ('eyelet_thickness', 3.5, 'Charm eyelet thickness'),
    ('serration_depth', 0.8, 'Depth of the slide grooves'),
    ('readout_depth', 1.5, 'Depth of the readout window recess'),
]

# Colours from the sketch (R, G, B), by body name
CREAM = (252, 240, 185)
BODY_COLORS = {
    'Slide': (232, 72, 170),
    'Barrel': (246, 160, 210),
    'Muzzle lip': CREAM,
    'Heart flange': (250, 196, 236),
    'Flange inset': CREAM,
    'Frame & Grip': (250, 190, 228),
    'Grip panel': (238, 112, 190),
    'Grip pin': (190, 45, 135),
    'Trigger': (200, 70, 160),
    'Top button': (225, 60, 150),
    'Heart cap': (240, 196, 240),
    'Heart inset': CREAM,
    'Charm': (215, 55, 145),
}


# =============================================================================
# 2D OUTLINES (pure geometry, no Fusion calls).
# A loop is a list of segments:
#   ('line', p0, p1)            straight line
#   ('arc', p0, pmid, p1)       arc through three points
#   ('spline', p0, p1, ... pn)  smooth curve through the points
#   ('circle', c, r)            full circle
# Points are (x, y) in the side view unless noted.
# =============================================================================

def _rot(p, deg):
    a = math.radians(deg)
    return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a))


def polygon(pts):
    return [('line', pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def transform(loop, deg=0.0, offset=(0.0, 0.0), scale=1.0):
    out = []
    for seg in loop:
        if seg[0] == 'circle':
            c = _rot(seg[1], deg)
            out.append(('circle', (c[0] * scale + offset[0], c[1] * scale + offset[1]), seg[2] * scale))
        else:
            pts = [_rot(p, deg) for p in seg[1:]]
            out.append((seg[0],) + tuple((p[0] * scale + offset[0], p[1] * scale + offset[1]) for p in pts))
    return out


def heart_shape(width):
    """Heart centred between its lobe centres, tip down: two circular lobes
    and two straight sides meeting at a point. Returns (loop, info)."""
    r = width / 3.2
    a = 0.6 * r                       # lobe centre offset from the middle
    h = 1.6 * r                       # tip depth below the lobe centres
    tip = (0.0, -h)
    cusp = (0.0, math.sqrt(r * r - a * a))

    def tangent_point(cx, outer_sign):
        dx, dy = tip[0] - cx, tip[1]
        d = math.hypot(dx, dy)
        base = math.atan2(dy, dx)
        off = math.acos(r / d)
        cands = [(cx + r * math.cos(base + s * off), r * math.sin(base + s * off)) for s in (1, -1)]
        return max(cands, key=lambda p: outer_sign * p[0])

    def arc_mid(cx, p0, p1):
        a0 = math.atan2(p0[1], p0[0] - cx)
        a1 = math.atan2(p1[1], p1[0] - cx)
        if a1 < a0:
            a1 += 2 * math.pi
        m = (a0 + a1) / 2
        return (cx + r * math.cos(m), r * math.sin(m))

    tr = tangent_point(a, +1)
    tl = tangent_point(-a, -1)
    loop = [
        ('line', tip, tr),
        ('arc', tr, arc_mid(a, tr, cusp), cusp),
        ('arc', cusp, arc_mid(-a, cusp, tl), tl),
        ('line', tl, tip),
    ]
    return loop, {'r': r, 'a': a, 'h': h, 'cusp_y': cusp[1]}


def heart(width, center=(0.0, 0.0), tilt_deg=0.0):
    return transform(heart_shape(width)[0], tilt_deg, center)


def heart_inset(width, center, tilt_deg, scale=INSET_SCALE):
    """Smaller heart inside a heart, nudged toward the tip so the rim is
    even all round."""
    info = heart_shape(width)[1]
    shift = _rot((0.0, -(1 - scale) * (info['h'] - info['r']) / 2.0), tilt_deg)
    return transform(heart_shape(width)[0], tilt_deg,
                     (center[0] + shift[0], center[1] + shift[1]), scale)


def circle_through(p0, p1, p2):
    ax, ay = p0
    bx, by = p1
    cx, cy = p2
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


def arc_band(p0, pm, p1, t_start, t_end):
    """Closed band along the arc p0 -> pm -> p1 that tapers from t_start to t_end."""
    c, _ = circle_through(p0, pm, p1)

    def off(p, t):
        ang = math.atan2(p[1] - c[1], p[0] - c[0])
        return (p[0] + t * math.cos(ang), p[1] + t * math.sin(ang))

    ts = (t_start / 2.0, (t_start + t_end) / 4.0, t_end / 2.0)
    o = [off(p, t) for p, t in zip((p0, pm, p1), ts)]
    i = [off(p, -t) for p, t in zip((p0, pm, p1), ts)]
    return [('arc', o[0], o[1], o[2]), ('line', o[2], i[2]), ('arc', i[2], i[1], i[0]), ('line', i[0], o[0])]


def slide_outline():
    L, H = SLIDE_LEN, SLIDE_H
    fx = L + SLIDE_FRONT_LEAN
    b = SLIDE_FRONT_BEVEL
    return polygon([(0, 0), (L, 0), (fx - b * SLIDE_FRONT_LEAN / H, H - b),
                    (fx - b * 1.6, H), (SLIDE_REAR_LEAN, H)])


def slide_rear_x(y):
    """x of the slanted rear face at height y."""
    return SLIDE_REAR_LEAN * y / SLIDE_H


def ears_outline():
    x0, y0 = EARS_X0, SLIDE_H - 1.0   # sinks 1 mm into the slide
    return polygon([(x0, y0), (x0 + EARS_LEN, y0), (x0 + 2.0, SLIDE_H + EARS_H)])


def serration_outlines():
    y0, y1 = 5.0, SLIDE_H - 5.0
    return [polygon([(x, y0), (x + SERRATION_W, y0),
                     (x + SERRATION_W + SERRATION_LEAN, y1), (x + SERRATION_LEAN, y1)])
            for x in SERRATION_XS]


def button_outline():
    x0, x1, y0, y1 = BUTTON_X0, BUTTON_X1, SLIDE_H - 0.5, SLIDE_H + BUTTON_H
    rr = (y1 - y0) / 2.0
    ym = (y0 + y1) / 2.0
    return [
        ('line', (x0 + rr, y0), (x1 - rr, y0)),
        ('arc', (x1 - rr, y0), (x1, ym), (x1 - rr, y1)),
        ('line', (x1 - rr, y1), (x0 + rr, y1)),
        ('arc', (x0 + rr, y1), (x0, ym), (x0 + rr, y0)),
    ]


def barrel_half_section():
    """Half cross-section revolved around y = BORE_AXIS_Y."""
    y = BORE_AXIS_Y
    x1 = MUZZLE_X1
    bb = x1 - BORE_DEPTH
    pts = [(bb, y), (BARREL_X0, y), (BARREL_X0, y + BARREL_R), (x1, y + BARREL_R),
           (x1, y + MUZZLE_LIP_R_IN), (x1 - 1.5, y + MUZZLE_LIP_R_IN),
           (x1 - 1.5, y + MUZZLE_RING_R), (x1 - 3.0, y + MUZZLE_RING_R),
           (x1 - 3.0, y + BORE_R), (bb, y + BORE_R)]
    return polygon(pts)


def muzzle_lip_half_section():
    """Cream lip ring standing 1.5 mm proud of the muzzle front."""
    y, x1 = BORE_AXIS_Y, MUZZLE_X1
    return polygon([(x1 - 2.0, y + MUZZLE_LIP_R_IN), (x1 + 1.5, y + MUZZLE_LIP_R_IN),
                    (x1 + 1.5, y + BARREL_R + 0.6), (x1 - 2.0, y + BARREL_R + 0.6)])


# Front-view outlines (u = across the gun, v = height) for the flange
def flange_loops():
    return [heart(FLANGE_HEART_W, (0.0, FLANGE_HEART_CY))]


def flange_inset_loops():
    return [heart_inset(FLANGE_HEART_W, (0.0, FLANGE_HEART_CY), 0.0)]


def front_sight_loops():
    cusp = FLANGE_HEART_CY + heart_shape(FLANGE_HEART_W)[1]['cusp_y']
    c = (0.0, cusp + SIGHT_LIFT)
    return [[('circle', c, SIGHT_R_OUT)], [('circle', c, SIGHT_R_IN)]]


def frame_outline():
    r, f, h = FRAME_REAR_X, FRAME_FRONT_X, FRAME_H
    return [
        ('line', (r, 0), (f, 0)),
        ('line', (f, 0), (f, -h * 0.55)),
        ('arc', (f, -h * 0.55), (f - 1.6, -h * 0.85), (f - 6, -h)),
        ('line', (f - 6, -h), (r, -h)),
        ('line', (r, -h), (r, 0)),
    ]


def readout_outline():
    return polygon([(READOUT_X0, READOUT_Y0), (READOUT_X1, READOUT_Y0),
                    (READOUT_X1, READOUT_Y1), (READOUT_X0, READOUT_Y1)])


def spine_rear_x(y):
    return SPINE_REAR_TOP_X + y * math.tan(math.radians(SPINE_REAR_RAKE))


def spine_front_x(y):
    return SPINE_FRONT_TOP_X + (y + FRAME_H) * math.tan(math.radians(SPINE_FRONT_RAKE))


def _unit(v):
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n)


def grip_outline():
    """Whole grip (back piece + panel) as one outline."""
    top = -4.0
    rear_top = (spine_rear_x(top), top)
    low = PANEL_FRONT[-1][1]                 # below GRIP_CUT_Y; trimmed off later
    rear_low = (spine_rear_x(low), low)
    return [
        ('line', rear_top, (FRAME_REAR_X, top)),
        ('line', (FRAME_REAR_X, top), (FRAME_REAR_X, PANEL_FRONT[0][1])),
        ('line', (FRAME_REAR_X, PANEL_FRONT[0][1]), PANEL_FRONT[0]),
        ('spline',) + tuple(PANEL_FRONT),
        ('line', PANEL_FRONT[-1], rear_low),
        ('line', rear_low, rear_top),
    ]


def grip_seam():
    """Line splitting the grip into the light back piece and the dark panel,
    running right through the base."""
    return [('line', (spine_front_x(0.0), 0.0), (spine_front_x(-90.0), -90.0))]


def guard_loops():
    h = FRAME_H
    fx, by = GUARD_OUT_FRONT_X, GUARD_OUT_BOTTOM_Y
    rear = PANEL_FRONT[0][0] - 8.0          # hidden inside the grip panel
    outer = [
        ('line', (rear, -h + 2), (fx, -h + 2)),
        ('arc', (fx, -h + 2), (fx + 8, (-h + by) / 2 + 2), (fx - 6, by)),
        ('line', (fx - 6, by), (rear, by)),
        ('line', (rear, by), (rear, -h + 2)),
    ]
    ir, ifx, iby = GUARD_IN_REAR_X, GUARD_IN_FRONT_X, GUARD_IN_BOTTOM_Y
    inner = [
        ('line', (ir, -h), (ifx, -h)),
        ('arc', (ifx, -h), (ifx + 6, (-h + iby) / 2 + 1), (ifx - 6, iby)),
        ('line', (ifx - 6, iby), (ir - 1, iby)),
        ('line', (ir - 1, iby), (ir, -h)),
    ]
    return [outer, inner]


def trigger_outline():
    h = FRAME_H
    return [
        ('line', (48, -h), (55, -h)),
        ('arc', (55, -h), (51, -h - 8), (56, -h - 15)),
        ('line', (56, -h - 15), (53, -h - 16.5)),
        ('arc', (53, -h - 16.5), (46, -h - 9), (48, -h)),
    ]


def eyelet_loops():
    c = EYELET_CENTER
    ring = [[('circle', c, EYELET_R_OUT)], [('circle', c, EYELET_R_IN)]]
    tab = polygon([(c[0] - 2.2, c[1] + EYELET_R_IN + 0.6), (c[0] + 2.2, c[1] + EYELET_R_IN + 0.6),
                   (c[0] + 2.2, -FRAME_H + 3), (c[0] - 2.2, -FRAME_H + 3)])
    return ring, tab


def cap_outline():
    return heart(CAP_HEART_W, CAP_CENTER, CAP_TILT_DEG)


def cap_inset_outline():
    return heart_inset(CAP_HEART_W, CAP_CENTER, CAP_TILT_DEG, CAP_INSET_SCALE)


def heart_lobes(width, center, tilt_deg, scale=1.0, inset=False):
    """The two lobes of a 3D heart as (tip, lobe_centre, radius). Each lobe
    is a ball with a cone running from it to the shared tip; together they
    have exactly the outline of heart()."""
    info = heart_shape(width)[1]
    r, a, h = info['r'] * scale, info['a'] * scale, info['h'] * scale
    shift = (0.0, 0.0)
    if inset:
        shift = _rot((0.0, -(1 - scale) * (info['h'] - info['r']) / 2.0), tilt_deg)
    ox, oy = center[0] + shift[0], center[1] + shift[1]

    def place(p):
        q = _rot(p, tilt_deg)
        return (q[0] + ox, q[1] + oy)
    tip = place((0.0, -h))
    return [(tip, place((a, 0.0)), r), (tip, place((-a, 0.0)), r)]


def lobe_half_section(tip, c, r):
    """Half outline of one lobe (cone + ball) to revolve around tip -> c.
    Returns (loop, axis_end)."""
    u = _unit((c[0] - tip[0], c[1] - tip[1]))
    d = math.hypot(c[0] - tip[0], c[1] - tip[1])
    theta = math.pi - math.acos(r / d)          # tangent point, measured from u

    def on_ball(ang):
        v = _rot(u, math.degrees(ang))
        return (c[0] + r * v[0], c[1] + r * v[1])
    p, mid, end = on_ball(theta), on_ball(theta / 2.0), on_ball(0.0)
    return [('line', tip, p), ('arc', p, mid, end), ('line', end, tip)], end


def heart_half_thickness(lobes, pt):
    """Half-thickness of an unscaled 3D heart at side-view point pt."""
    best = 0.0
    for tip, c, r in lobes:
        u = _unit((c[0] - tip[0], c[1] - tip[1]))
        d = math.hypot(c[0] - tip[0], c[1] - tip[1])
        vx, vy = pt[0] - tip[0], pt[1] - tip[1]
        s = vx * u[0] + vy * u[1]                       # distance along the axis
        rho = abs(vx * u[1] - vy * u[0])                # distance from the axis
        s_tan = (d * d - r * r) / d                     # where the cone meets the ball
        if s <= 0:
            continue
        if s <= s_tan:
            R = s * r / math.sqrt(d * d - r * r)
        elif s <= d + r:
            R = math.sqrt(max(r * r - (s - d) ** 2, 0.0))
        else:
            continue
        if rho < R:
            best = max(best, math.sqrt(R * R - rho * rho))
    return best


def cap_z_scales():
    """Z (side-to-side) squash for the cap and for its cream centre, so the
    cap is CAP_DEPTH thick and the centre bulges CAP_INSET_PROUD out."""
    big = heart_lobes(CAP_HEART_W, CAP_CENTER, CAP_TILT_DEG)
    small = heart_lobes(CAP_HEART_W, CAP_CENTER, CAP_TILT_DEG, CAP_INSET_SCALE, inset=True)
    zs = CAP_DEPTH / (2.0 * big[0][2])
    peak = small[0][1]
    zs_in = (zs * heart_half_thickness(big, peak) + CAP_INSET_PROUD) / small[0][2]
    return zs, zs_in


def grip_loop_outline():
    return arc_band(LOOP_START, LOOP_MID, LOOP_END, LOOP_T_START, LOOP_T_END)


def charm_loops():
    """Heart with a keyhole cut through it (a heart padlock)."""
    cx, cy = CHARM_CENTER
    kc = (cx, cy - 1.0)               # keyhole circle centre
    kr = 1.9
    half = 0.9
    ky = kc[1] - math.sqrt(kr * kr - half * half)
    keyhole = [
        ('arc', (cx + half, ky), (cx, kc[1] + kr), (cx - half, ky)),
        ('line', (cx - half, ky), (cx - 1.5, cy - 6.0)),
        ('line', (cx - 1.5, cy - 6.0), (cx + 1.5, cy - 6.0)),
        ('line', (cx + 1.5, cy - 6.0), (cx + half, ky)),
    ]
    return [heart(CHARM_W, CHARM_CENTER), keyhole]


def charm_bail_loops():
    """Small ring on top of the charm for the chain."""
    cx, cy = CHARM_CENTER
    r = heart_shape(CHARM_W)[1]['r']
    c = (cx, cy + r + 0.8)
    return [[('circle', c, 2.5)], [('circle', c, 1.3)]]


# =============================================================================
# FUSION HELPERS
# =============================================================================

X_SIGN = -1.0   # mirror so the muzzle points to -X (left side faces the Front view)
_skipped = []   # things that could not be built (shown at the end)


def cm(v_mm):
    return v_mm / 10.0


def vi(v):
    """ValueInput from a number (mm) or a parameter expression string."""
    if isinstance(v, str):
        return adsk.core.ValueInput.createByString(v)
    return adsk.core.ValueInput.createByReal(cm(v))


def sk_point(sketch, x, y, z):
    p = sketch.modelToSketchSpace(adsk.core.Point3D.create(cm(X_SIGN * x), cm(y), cm(z)))
    return adsk.core.Point3D.create(p.x, p.y, 0)


def draw_loops(sketch, loops, to3d):
    """Draw loops into a sketch. to3d maps an outline point to (x, y, z) mm."""
    curves = sketch.sketchCurves
    for loop in loops:
        for seg in loop:
            kind = seg[0]
            if kind == 'circle':
                c = sk_point(sketch, *to3d(seg[1]))
                curves.sketchCircles.addByCenterRadius(c, cm(seg[2]))
            elif kind == 'line':
                curves.sketchLines.addByTwoPoints(sk_point(sketch, *to3d(seg[1])),
                                                  sk_point(sketch, *to3d(seg[2])))
            elif kind == 'arc':
                curves.sketchArcs.addByThreePoints(sk_point(sketch, *to3d(seg[1])),
                                                   sk_point(sketch, *to3d(seg[2])),
                                                   sk_point(sketch, *to3d(seg[3])))
            elif kind == 'spline':
                pts = adsk.core.ObjectCollection.create()
                for p in seg[1:]:
                    pts.add(sk_point(sketch, *to3d(p)))
                curves.sketchFittedSplines.add(pts)
    _merge_endpoints(sketch)


def _merge_endpoints(sketch, tol=1e-5):
    """Join coincident curve ends so loops are properly connected."""
    pts = [sketch.sketchPoints.item(i) for i in range(sketch.sketchPoints.count)]
    keep = []
    for sp in pts:
        try:
            if not sp.isValid:
                continue
            g = sp.geometry
            target = None
            for k in keep:
                if k.isValid and k.geometry.distanceTo(g) < tol:
                    target = k
                    break
            if target is not None:
                target.merge(sp)
            else:
                keep.append(sp)
        except Exception:
            pass


def side_sketch(comp, name, loops, plane=None):
    """Sketch side-view loops (x, y) on the XY plane or a plane parallel to it."""
    sk = comp.sketches.add(plane or comp.xYConstructionPlane)
    sk.name = name
    draw_loops(sk, loops, lambda p: (p[0], p[1], 0.0))
    return sk


def front_sketch(comp, name, loops, x):
    """Sketch front-view loops (u = across, v = height) on a plane at x."""
    sk = comp.sketches.add(x_plane(comp, x))
    sk.name = name
    draw_loops(sk, loops, lambda p: (x, p[1], p[0]))
    return sk


def pick_profile(sketch, loops=None):
    """Largest profile, or the largest one with the given number of loops."""
    best, best_area = None, -1.0
    for i in range(sketch.profiles.count):
        pr = sketch.profiles.item(i)
        if loops is not None and pr.profileLoops.count != loops:
            continue
        area = pr.areaProperties(adsk.fusion.CalculationAccuracy.LowCalculationAccuracy).area
        if area > best_area:
            best, best_area = pr, area
    if best is None:
        raise RuntimeError('No suitable profile found in sketch "{}"'.format(sketch.name))
    return best


def all_profiles(sketch):
    coll = adsk.core.ObjectCollection.create()
    for i in range(sketch.profiles.count):
        coll.add(sketch.profiles.item(i))
    return coll


def extrude_sym(comp, profile, width, op, participants=None, name=None):
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(profile, op)
    inp.setSymmetricExtent(vi(width), True)
    if participants:
        inp.participantBodies = participants
    feat = ext.add(inp)
    if name and feat.bodies.count and op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        feat.bodies.item(0).name = name
    return feat


def revolve_new(comp, sketch, name, axis_from=None, axis_to=None):
    """Revolve the sketch's largest profile 360 degrees around a side-view
    axis (default: the bore axis)."""
    a0 = axis_from or (BARREL_X0, BORE_AXIS_Y)
    a1 = axis_to or (MUZZLE_X1, BORE_AXIS_Y)
    axis = sketch.sketchCurves.sketchLines.addByTwoPoints(
        sk_point(sketch, a0[0], a0[1], 0.0), sk_point(sketch, a1[0], a1[1], 0.0))
    axis.isConstruction = True
    revs = comp.features.revolveFeatures
    inp = revs.createInput(pick_profile(sketch), axis, NEW)
    inp.setAngleExtent(False, adsk.core.ValueInput.createByString('360 deg'))
    body = revs.add(inp).bodies.item(0)
    body.name = name
    return body


def offset_plane(comp, base, expr, axis, expected_mm):
    """Offset construction plane. Checks it landed on the expected side and
    flips it if Fusion's normal points the other way."""
    planes = comp.constructionPlanes

    def make(e):
        inp = planes.createInput()
        inp.setByOffset(base, vi(e))
        return planes.add(inp)

    pl = make(expr)
    o = pl.geometry.origin
    got = {'x': o.x, 'y': o.y, 'z': o.z}[axis] * 10.0
    if expected_mm != 0 and (got > 0) != (expected_mm > 0):
        pl.deleteMe()
        pl = make('-(' + expr + ')' if isinstance(expr, str) else -expr)
    return pl


def x_plane(comp, x):
    """Plane square to the barrel at outline position x (mm)."""
    return offset_plane(comp, comp.yZConstructionPlane, X_SIGN * x, 'x', X_SIGN * x)


def combine_join(comp, target, tools):
    if not tools:
        return
    coll = adsk.core.ObjectCollection.create()
    for t in tools:
        coll.add(t)
    inp = comp.features.combineFeatures.createInput(target, coll)
    inp.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    inp.isKeepToolBodies = False
    comp.features.combineFeatures.add(inp)


def fillet(comp, body, radius, label, edge_filter=None):
    """Try to fillet the body's edges; halve the radius once on failure."""
    for r in (radius, radius / 2.0):
        edges = adsk.core.ObjectCollection.create()
        for i in range(body.edges.count):
            e = body.edges.item(i)
            if edge_filter is None or edge_filter(e):
                edges.add(e)
        if edges.count == 0:
            return
        try:
            fillets = comp.features.filletFeatures
            inp = fillets.createInput()
            try:
                inp.edgeSetInputs.addConstantRadiusEdgeSet(edges, vi(r), True)
            except AttributeError:
                inp.addConstantRadiusEdgeSet(edges, vi(r), True)
            fillets.add(inp)
            if r != radius:
                _skipped.append('{}: fillet reduced to {:.1f} mm'.format(label, r))
            return
        except Exception:
            continue
    _skipped.append('{}: fillet skipped'.format(label))


def flat_in(axis):
    """Edge filter: edges lying flat on a face square to `axis`. Use for
    outlines with smooth (tangent) joins, whose straight-through edges
    can't be filleted."""
    def f(edge):
        bb = edge.boundingBox
        lo = {'x': bb.minPoint.x, 'y': bb.minPoint.y, 'z': bb.minPoint.z}[axis]
        hi = {'x': bb.maxPoint.x, 'y': bb.maxPoint.y, 'z': bb.maxPoint.z}[axis]
        return abs(hi - lo) < 1e-4
    return f


def new_component(root, name):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def bodies(comp):
    return [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]


def body_named(comp, name):
    for b in bodies(comp):
        if b.name == name:
            return b
    raise RuntimeError('Body "{}" not found'.format(name))


NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation


# =============================================================================
# PART BUILDERS
# =============================================================================

def build_slide(root):
    comp = new_component(root, 'Slide')
    sk = side_sketch(comp, 'Slide profile', [slide_outline()])
    slide = extrude_sym(comp, pick_profile(sk), 'slide_width', NEW, name='Slide').bodies.item(0)
    fillet(comp, slide, FILLET_SLIDE, 'Slide')

    # Cat ears: a wedge with a notch cut down the middle
    sk = side_sketch(comp, 'Ears profile', [ears_outline()])
    ears = extrude_sym(comp, pick_profile(sk), 'slide_width - 4 mm', NEW, name='Ears').bodies.item(0)
    sk = front_sketch(comp, 'Ears notch', [polygon([
        (-EARS_GAP / 2, SLIDE_H + 0.5), (EARS_GAP / 2, SLIDE_H + 0.5),
        (EARS_GAP / 2, SLIDE_H + EARS_H + 5), (-EARS_GAP / 2, SLIDE_H + EARS_H + 5)])],
        EARS_X0 + EARS_LEN / 2)
    extrude_sym(comp, pick_profile(sk), EARS_LEN * 3, CUT, participants=[ears])
    fillet(comp, body_named(comp, 'Ears'), 0.6, 'Ears', edge_filter=lambda e: e.boundingBox.minPoint.y * 10 > SLIDE_H + 0.2)
    slide = body_named(comp, 'Slide')
    combine_join(comp, slide, [b for b in bodies(comp) if b.name != 'Slide'])
    slide = body_named(comp, 'Slide')

    # Slanted grooves on both sides
    for side, label in ((1, 'right'), (-1, 'left')):
        expr = 'slide_width / 2' if side > 0 else '-slide_width / 2'
        pl = offset_plane(comp, comp.xYConstructionPlane, expr, 'z', side * 14.0)
        sk = side_sketch(comp, 'Grooves ({})'.format(label), serration_outlines(), plane=pl)
        try:
            extrude_sym(comp, all_profiles(sk), 'serration_depth * 2', CUT, participants=[slide])
        except Exception:
            _skipped.append('Slide: {} grooves skipped'.format(label))
    return comp


def build_muzzle(root):
    comp = new_component(root, 'Muzzle & Shroud')
    revolve_new(comp, side_sketch(comp, 'Barrel half-section', [barrel_half_section()]), 'Barrel')
    revolve_new(comp, side_sketch(comp, 'Muzzle lip half-section', [muzzle_lip_half_section()]),
                'Muzzle lip')

    # Heart flange (the shroud) with its cream inset and the front sight ring
    mid = FLANGE_X + FLANGE_T / 2.0
    sk = front_sketch(comp, 'Heart flange', flange_loops(), mid)
    flange = extrude_sym(comp, pick_profile(sk), 'flange_width', NEW, name='Heart flange').bodies.item(0)
    fillet(comp, flange, 1.5, 'Heart flange', edge_filter=flat_in('x'))
    sk = front_sketch(comp, 'Front sight ring', front_sight_loops(), mid)
    flange = body_named(comp, 'Heart flange')
    extrude_sym(comp, pick_profile(sk, loops=2), 'sight_thickness', JOIN, participants=[flange])
    front = FLANGE_X + FLANGE_T
    sk = front_sketch(comp, 'Flange inset', flange_inset_loops(), front)
    extrude_sym(comp, pick_profile(sk), 'inset_proud * 2', NEW, name='Flange inset')
    fillet(comp, body_named(comp, 'Flange inset'), 0.6, 'Flange inset', edge_filter=flat_in('x'))
    return comp


def build_frame(root):
    comp = new_component(root, 'Frame & Grip')

    sk = side_sketch(comp, 'Frame profile', [frame_outline()])
    frame = extrude_sym(comp, pick_profile(sk), 'frame_width', NEW, name='Frame').bodies.item(0)
    fillet(comp, frame, FILLET_FRAME, 'Frame')

    # Grip: one body ending in a flat oval base, then split into the light
    # back strip and the dark panel (flush, both running into the base).
    sk = side_sketch(comp, 'Grip profile', [grip_outline()])
    grip = extrude_sym(comp, pick_profile(sk), 'grip_width', NEW, name='Grip').bodies.item(0)
    fillet(comp, grip, FILLET_GRIP, 'Grip',
           edge_filter=lambda e: flat_in('z')(e) and e.boundingBox.minPoint.y * 10 < -FRAME_H - 1)
    add_oval_base(comp)
    split_grip(comp)
    sk = side_sketch(comp, 'Grip pin', [[('circle', GRIP_PIN, GRIP_PIN_R)]])
    extrude_sym(comp, pick_profile(sk), 'grip_width + 2 mm', NEW, name='Grip pin')

    sk = side_sketch(comp, 'Trigger guard profile', guard_loops())
    guard = extrude_sym(comp, pick_profile(sk, loops=2), 'guard_width', NEW, name='Guard').bodies.item(0)
    fillet(comp, guard, FILLET_GUARD, 'Trigger guard')

    ring_loops, tab = eyelet_loops()
    sk = side_sketch(comp, 'Charm eyelet', ring_loops)
    extrude_sym(comp, pick_profile(sk, loops=2), 'eyelet_thickness', NEW, name='Eyelet')
    sk = side_sketch(comp, 'Charm eyelet tab', [tab])
    extrude_sym(comp, pick_profile(sk), 'eyelet_thickness', NEW, name='Eyelet tab')

    frame = body_named(comp, 'Frame')
    combine_join(comp, frame, [b for b in bodies(comp)
                               if b.name not in ('Frame', 'Grip panel', 'Grip pin')])
    frame = body_named(comp, 'Frame')
    frame.name = 'Frame & Grip'

    # Readout window recess on the left side (+Z after mirroring)
    pl = offset_plane(comp, comp.xYConstructionPlane, 'frame_width / 2', 'z', 11.0)
    sk = side_sketch(comp, 'Readout window', [readout_outline()], plane=pl)
    extrude_sym(comp, pick_profile(sk), 'readout_depth * 2', CUT, participants=[frame])
    return comp


def split_grip(comp):
    """Split the 'Grip' body along the colour seam into 'Spine' (back) and
    'Grip panel' (front)."""
    grip = body_named(comp, 'Grip')
    sk = side_sketch(comp, 'Grip seam', [grip_seam()])
    prof = comp.createOpenProfile(sk.sketchCurves.sketchLines.item(0), True)
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(prof, NEW)
    inp.isSolid = False
    inp.setSymmetricExtent(vi(80.0), True)
    surf = ext.add(inp).bodies.item(0)
    splits = comp.features.splitBodyFeatures
    splits.add(splits.createInput(grip, surf, True))
    try:
        comp.features.removeFeatures.add(surf)
    except Exception:
        surf.isLightBulbOn = False
    halves = [b for b in bodies(comp) if b.isSolid and b.name != 'Frame']

    def reach(b):     # how far toward the muzzle the body goes (outline x)
        bb = b.boundingBox
        return max(X_SIGN * bb.minPoint.x, X_SIGN * bb.maxPoint.x)
    halves.sort(key=reach)
    halves[0].name = 'Spine'
    halves[-1].name = 'Grip panel'


def add_oval_base(comp):
    """Trim the grip flat at GRIP_CUT_Y and loft from there to a flat oval
    at GRIP_BASE_Y."""
    grip = body_named(comp, 'Grip')
    pl = offset_plane(comp, comp.xZConstructionPlane, GRIP_CUT_Y, 'y', GRIP_CUT_Y)
    splits = comp.features.splitBodyFeatures
    splits.add(splits.createInput(grip, pl, True))
    for b in bodies(comp):
        if b.name != 'Frame' and b.boundingBox.maxPoint.y * 10 < GRIP_CUT_Y + 0.01:
            comp.features.removeFeatures.add(b)
    grip = [b for b in bodies(comp) if b.name != 'Frame'][0]
    grip.name = 'Grip'
    section = None
    for i in range(grip.faces.count):
        f = grip.faces.item(i)
        plane = adsk.core.Plane.cast(f.geometry)
        if plane and abs(abs(plane.normal.y) - 1.0) < 1e-6 and abs(f.pointOnFace.y * 10 - GRIP_CUT_Y) < 0.01:
            section = f
            break
    if section is None:
        raise RuntimeError('Could not find the grip cut face for the oval base')

    bpl = offset_plane(comp, comp.xZConstructionPlane, GRIP_BASE_Y, 'y', GRIP_BASE_Y)
    sk = comp.sketches.add(bpl)
    sk.name = 'Oval base'
    cx, y = BASE_CENTER_X, GRIP_BASE_Y
    sk.sketchCurves.sketchEllipses.add(sk_point(sk, cx, y, 0.0),
                                       sk_point(sk, cx + BASE_LENGTH / 2.0, y, 0.0),
                                       sk_point(sk, cx, y, BASE_WIDTH / 2.0))
    lofts = comp.features.loftFeatures
    inp = lofts.createInput(NEW)
    inp.loftSections.add(section)
    inp.loftSections.add(pick_profile(sk))
    inp.isSolid = True
    base = lofts.add(inp).bodies.item(0)
    base.name = 'Base'
    combine_join(comp, body_named(comp, 'Grip'), [base])
    grip = body_named(comp, 'Grip')
    fillet(comp, grip, 3.0, 'Oval base edge',
           edge_filter=lambda e: e.boundingBox.maxPoint.y * 10 < GRIP_BASE_Y + 0.1)


def build_trigger(root):
    comp = new_component(root, 'Trigger')
    sk = side_sketch(comp, 'Trigger profile', [trigger_outline()])
    body = extrude_sym(comp, pick_profile(sk), 'trigger_width', NEW, name='Trigger').bodies.item(0)
    top = -FRAME_H / 10.0 - 0.05
    fillet(comp, body, FILLET_SMALL, 'Trigger', edge_filter=lambda e: e.boundingBox.maxPoint.y < top)
    return comp


def build_button(root):
    comp = new_component(root, 'Top Button')
    sk = side_sketch(comp, 'Button profile', [button_outline()])
    body = extrude_sym(comp, pick_profile(sk), 'button_width', NEW, name='Top button').bodies.item(0)
    fillet(comp, body, 2.0, 'Top button', edge_filter=flat_in('z'))
    return comp


def build_rear_cap(root):
    comp = new_component(root, 'Rear Cap (Heart)')
    zs, zs_in = cap_z_scales()
    build_3d_heart(comp, 'Heart cap', heart_lobes(CAP_HEART_W, CAP_CENTER, CAP_TILT_DEG), zs)
    build_3d_heart(comp, 'Heart inset',
                   heart_lobes(CAP_HEART_W, CAP_CENTER, CAP_TILT_DEG, CAP_INSET_SCALE, inset=True), zs_in)
    if INCLUDE_GRIP_LOOP:
        sk = side_sketch(comp, 'Grip loop profile', [grip_loop_outline()])
        loop = extrude_sym(comp, pick_profile(sk), 'loop_width', NEW, name='Grip loop').bodies.item(0)
        fillet(comp, loop, 2.5, 'Grip loop')
        cap = body_named(comp, 'Heart cap')
        combine_join(comp, cap, [body_named(comp, 'Grip loop')])
    return comp


def build_3d_heart(comp, name, lobes, z_scale):
    """Puffy heart: each lobe is a ball + cone revolved to the shared tip;
    the two are joined, then squashed side to side to the wanted thickness."""
    made = []
    for i, (tip, c, r) in enumerate(lobes):
        loop, end = lobe_half_section(tip, c, r)
        sk = side_sketch(comp, '{} lobe {}'.format(name, i + 1), [loop])
        made.append(revolve_new(comp, sk, '{} lobe {}'.format(name, i + 1), tip, end))
    combine_join(comp, made[0], made[1:])
    body = body_named(comp, '{} lobe 1'.format(name))
    body.name = name
    try:
        coll = adsk.core.ObjectCollection.create()
        coll.add(body)
        scales = comp.features.scaleFeatures
        inp = scales.createInput(coll, comp.originConstructionPoint, adsk.core.ValueInput.createByReal(1.0))
        one = adsk.core.ValueInput.createByReal(1.0)
        inp.setToNonUniform(one, one, adsk.core.ValueInput.createByReal(z_scale))
        scales.add(inp)
    except Exception:
        _skipped.append('{}: could not squash it side to side, so it is fully round'.format(name))
    return body


def build_charm(root):
    comp = new_component(root, 'Charm')
    sk = side_sketch(comp, 'Charm profile', charm_loops())
    body = extrude_sym(comp, pick_profile(sk, loops=2), 'charm_thickness', NEW, name='Charm').bodies.item(0)
    fillet(comp, body, FILLET_SMALL, 'Charm', edge_filter=lambda e: flat_in('z')(e)
           and e.boundingBox.maxPoint.x - e.boundingBox.minPoint.x > 0.45)   # skip the keyhole
    sk = side_sketch(comp, 'Charm bail', charm_bail_loops())
    extrude_sym(comp, pick_profile(sk, loops=2), 'charm_thickness / 2', JOIN,
                participants=[body_named(comp, 'Charm')])
    return comp


# =============================================================================
# APPEARANCE (best effort: skipped quietly if the library isn't available)
# =============================================================================

def apply_colors(app, design, comps):
    try:
        base = None
        for i in range(app.materialLibraries.count):
            lib = app.materialLibraries.item(i)
            if 'appearance' not in lib.name.lower():
                continue
            for j in range(lib.appearances.count):
                ap = lib.appearances.item(j)
                if ap.name.startswith('Plastic - Glossy'):
                    base = ap
                    break
            if base:
                break
        if base is None:
            return
        made = {}
        for comp in comps:
            for b in bodies(comp):
                rgb = BODY_COLORS.get(b.name)
                if not rgb:
                    continue
                if rgb not in made:
                    ap = design.appearances.addByCopy(base, 'Celestia {} {} {}'.format(*rgb))
                    for k in range(ap.appearanceProperties.count):
                        prop = adsk.core.ColorProperty.cast(ap.appearanceProperties.item(k))
                        if prop:
                            prop.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
                            break
                    made[rgb] = ap
                b.appearance = made[rgb]
    except Exception:
        _skipped.append('Colours skipped (appearance library unavailable)')


# =============================================================================
# ENTRY POINT
# =============================================================================

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        _skipped.clear()

        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        root = design.rootComponent

        for name, value, comment in LIVE_PARAMS:
            design.userParameters.add(name, adsk.core.ValueInput.createByString('{} mm'.format(value)),
                                      'mm', comment)

        comps = []
        for label, builder in (('Slide', build_slide), ('Muzzle & Shroud', build_muzzle),
                               ('Frame & Grip', build_frame),
                               ('Trigger', build_trigger), ('Top Button', build_button),
                               ('Rear Cap (Heart)', build_rear_cap), ('Charm', build_charm)):
            try:
                comps.append(builder(root))
            except Exception:
                _skipped.append('{} FAILED:\n{}'.format(label, traceback.format_exc(limit=2)))

        apply_colors(app, design, comps)
        app.activeViewport.fit()

        msg = 'CYBER Celestia CGM built: {} parts.'.format(len(comps))
        if _skipped:
            msg += '\n\nNotes:\n- ' + '\n- '.join(_skipped)
        msg += '\n\nWidths and depths: Modify > Change Parameters.'
        ui.messageBox(msg, 'CYBER Celestia CGM')
    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
