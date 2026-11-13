"""
CYBER Celestia - Custom Gun Mouse (CGM)
Starter model for Autodesk Fusion, built from concept sketch v1
(reference/concept-sketch-v1.webp).

HOW TO RUN
  Utilities > Add-Ins > Scripts and Add-Ins > "+" (Script or add-in from
  device) > pick this folder > select CelestiaGunMouse > Run.
  The script always opens a NEW design, so it never touches your other work.

WHAT YOU GET (one component per part of the sketch)
  Slide (grooves), Muzzle & Shroud (barrel, heart flange, front sight ring,
  muzzle rings), Frame & Grip (one light-pink piece: top strip, cat ears,
  frame, readout window, trigger guard, grip back strip, grip loop, charm
  eyelet; plus the dark grip panel and oval base), Trigger, Reload Button
  (top), Infuse Button and Recenter Button (left side), LED Window,
  Rear Cap (puffy 3D heart) and Charm (heart padlock).
  The slide, frame and grip are hollow inside (one connected space) for the
  electronics, with a pocket behind the readout window. Openings for the LED stick, buttons, readout and a USB-C port on
  the grip's right side (see "Inside the gun" in DIMENSIONS).

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

# Shown in the pop-up at the end of a run, so you can tell which version ran.
SCRIPT_VERSION = 'v18: mounts for the switches, Nano, IMU and LED stick'

import adsk.core
import adsk.fusion


# =============================================================================
# DIMENSIONS (mm). Edit these, then re-run the script.
# =============================================================================

# Slide: a parallelogram whose front and rear ends lean forward at the top
SLIDE_LEN = 134.0           # along the bottom edge
SLIDE_H = 32.0
# Seen from the front the slide's dark magenta sides ("shields") lean out
# toward the bottom as single flat faces.
SLIDE_TOP_W = 24.0          # width across the top of the slide
SLIDE_SIDE_ANGLE = 8.0      # lean of the sides from vertical (bigger = more angled)
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

# Light-pink strip wrapping the top and slanted back of the slide. It is one
# piece with the ears, frame, grip back strip and grip loop (no seams).
TOP_STRIP_H = 3.0           # thickness of the strip along the top
REAR_STRIP_W = 5.0          # width of the strip down the slanted back

# Reload button (pill on top of the slide)
BUTTON_X0, BUTTON_X1 = 40.0, 54.0   # the reload button (pill on top of the slide)
BUTTON_H = 5.0
RELOAD_W = 9.0                      # its width, side to side

# ---- Inside the gun (parts from the "Gun Controller - Parts Rundown" doc) ----
# Measure your parts with calipers when they arrive and adjust these.
WALL = 2.5                  # shell wall thickness
CLEAR = 0.25                # gap around moving parts and lids
SLIDE_CAVITY_TOP = SLIDE_H - TOP_STRIP_H - 2.0   # inside roof of the slide
# The frame is hollow inside too (one connected space with the slide and grip),
# with a pocket behind the readout window under a thin lip.
FRAME_CAVITY_X = (8.0, 124.0)     # hollow inside the frame, back to front
READOUT_LIP = 1.0                 # thin rim round the window that hides a screen's edges
READOUT_POCKET_DEPTH = 8.0        # how deep the pocket goes into the frame
GRIP_CAVITY_BOTTOM = -52.0                        # hollow grip goes down to here
GRIP_CAVITY_HALF_W = 11.5                         # half width of the grip hollow (23 mm: board is 21.7)
# Arduino Nano ESP32 (45 x 18 mm, ~5 mm thick without headers) stands upright
# in the grip, USB-C end down; the port opens through the bottom of the base.
# A pocket in the base holds its USB end; tape or hot-glue the top in place.
# The Pololu LSM6DS33 IMU (23 x 13 mm) sits in the slide, wired with 4 wires.
BOARD_SIZE = (45.0, 18.0, 5.0)    # length, width, thickness
BOARD_X = 0.0                     # front-back position of the board's centre
BOARD_FLOOR = 1.5                 # plastic under the board's USB end
USB_HOLE = (7.5, 13.5)            # opening for the plug (front-back, side-to-side)
# NeoPixel stick (51.1 x 10.2 x 3.2 mm) on top of the slide between the wings,
# under a translucent window printed in clear/natural PETG.
LED_WINDOW_X = (62.0, 114.0)
LED_WINDOW_W = 11.0
# 12 mm tactile buttons: reload = the pill on top, infuse and recenter are
# round caps on the left side where your thumb rests.
INFUSE_POS = (30.0, 14.0)         # on the slide's left side
RECENTER_POS = (3.0, -17.5)       # on the grip's left side, above the Nano
SIDE_BUTTON_D = 10.0
SIDE_BUTTON_PROUD = 1.5           # how far the round caps stick out
TACT_H = 7.3                      # total height of your 12 mm tactile buttons (body + plunger)
TACT_SEAT = -0.2                  # side-button switches sit on columns in the RIGHT half, ending here
# Where the IMU board lies, flat on the frame floor, lined up with the barrel
IMU_SIZE = (22.9, 12.7)           # Pololu LSM6DS33 carrier
IMU_X = 63.5                      # its centre, front-back

# Trigger and ADS levers. Each swings on a 3 mm steel pin; pulling it pushes
# a nub at its back through a slot in the grip front onto a lever
# microswitch (~20 x 10 x 6 mm) lying across the grip, lever facing forward.
PIVOT_PIN_R = 1.6                 # hole in the shell for the 3 mm pin
TRIGGER_PIVOT = (42.0, -6.0)      # inside the frame
ADS_PIVOT = (33.0, -24.5)         # inside the grip front, under the trigger
TRIGGER_SWITCH = (19.0, 29.0, -19.0, -13.0)   # x0, x1, y0, y1 of the switch body
ADS_SWITCH = (18.0, 28.0, -34.0, -28.0)
SWITCH_HALF_LEN = 10.0            # half its 20 mm length (it lies across the grip)

# Left/right split. How the halves are held together:
#   'standoff' - your 4 M3 nylon standoffs (13 mm body, 6 mm male thread, M/F)
#                with their nuts. Each standoff sits hidden in a hex pocket in
#                the LEFT half; its thread pokes into the RIGHT half, where the
#                nut goes on through a hole for a 5.5 mm nut driver. Glue each
#                colour piece to its neighbour on the same side first.
#   'screw'    - 6 M3 screws from the RIGHT side into heat-set inserts.
FASTENER = 'standoff'
STANDOFF_POSTS = {
    'Slide': [(120.0, 5.5), (14.0, 5.5)],
    'Frame & Grip': [(-16.0, -50.0)],
    'Grip panel': [(12.0, -40.0)],
}
STANDOFF_POST_R = 5.5
STANDOFF_LEN = 13.0                   # hex body length
STANDOFF_HEX_AF = 5.0                 # across the flats of the hex body
STUD_LEN = 6.0                        # male thread length
NUT_T = 2.4                           # M3 nut thickness
NUT_DRIVER_R = 4.0                    # hole for a 5.5 mm nut driver
SCREW_POSTS = {
    'Slide': [(120.0, 4.0), (120.0, 22.0), (14.0, 4.0)],
    'Frame & Grip': [(72.0, -3.5), (-16.0, -50.0)],
    'Grip panel': [(12.0, -40.0)],
}
POST_R = 3.5
INSERT_R, INSERT_DEPTH = 2.0, 5.7     # M3 heat-set insert hole
SCREW_CLEAR_R = 1.7                   # M3 clearance hole
HEAD_R, HEAD_DEPTH = 3.0, 3.2         # recess for the screw head

# Barrel and muzzle (revolved around a horizontal axis)
BORE_AXIS_Y = 11.0          # height of the barrel centreline
BARREL_R = 15.0
BARREL_X0 = 128.0           # starts inside the slide
FLANGE_X = 162.0            # rear face of the heart flange (the "shroud")
FLANGE_T = 6.0              # flange thickness
MUZZLE_X1 = 184.0           # front face of the muzzle
MUZZLE_LIP_R_IN = 10.5      # light-pink lip ring on the muzzle front
MUZZLE_RING_R = 9.0         # inner ring step
BORE_R = 7.0
BORE_DEPTH = 15.0

MUZZLE_R = 13.0             # muzzle in front of the heart flange

# Heart flange (shroud) around the barrel, tip pointing down
FLANGE_HEART_W = 52.0
FLANGE_HEART_CY = 21.0      # height of the line between the two lobes

# Front sight: two horns (an open ring) in the heart's top dip, with a bead
SIGHT_R_OUT = 10.0
SIGHT_R_IN = 6.0
SIGHT_LIFT = 6.0            # horn ring centre above the heart's dip
SIGHT_GAP_DEG = 25.0        # half-angle of the opening between the horn tips
SIGHT_BEAD_R = 3.0

# Frame (strip under the slide)
FRAME_REAR_X = 4.0
FRAME_FRONT_X = 128.0
FRAME_H = 12.0
# The light-pink frame is a plain rectangle seen from the front (straight
# sides, flat bottom), as wide as the bottom of the slide.

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
GUARD_OUT_BOTTOM_Y = -40.0  # taller opening: the trigger AND the ADS lever fit inside
GUARD_IN_REAR_X = 38.0
GUARD_IN_FRONT_X = 66.0
GUARD_IN_BOTTOM_Y = -36.0
GUARD_WEB_DROP = 11.0       # how far down the grip front the guard blends in

# Heart rear cap: a puffy 3D heart (doubles as a palm rest)
CAP_CENTER = (-8.0, 18.0)   # midway between the two lobe centres
CAP_HEART_W = 58.0          # lobe-to-lobe width before tilting
CAP_TILT_DEG = 40.0         # tilts the tip forward/down into the slide
CAP_DEPTH = 30.0            # thickness at the middle of the heart
CAP_INSET_SCALE = 0.85      # size of the cream heart inside the cap
CAP_INSET_PROUD = 2.0       # how far the cream centre bulges out of each side
INSET_SCALE = 0.8           # cream inner heart size on the flange

# Grip loop: tapered band from the heart down into the grip back piece
INCLUDE_GRIP_LOOP = True
LOOP_START = (-20.0, -2.0)  # inside the heart's rear lobe
LOOP_MID = (-11.5, -14.0)   # bows in toward the grip (bigger first number = more)
LOOP_END = (-8.0, -30.0)    # well inside the back of the grip, so it fuses on
LOOP_T_START, LOOP_T_END = 6.0, 4.5

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
    ('grip_width', 30.0, 'Grip panel (dark pink) thickness, side to side'),
    ('guard_width', 12.0, 'Trigger guard thickness'),
    ('trigger_width', 7.0, 'Trigger blade thickness'),
    ('flange_width', 6.0, 'Heart flange (shroud) thickness'),
    ('inset_proud', 1.5, 'How far the cream heart insets stand out'),
    ('loop_width', 8.0, 'Grip loop thickness'),
    ('sight_thickness', 3.0, 'Front sight ring thickness'),
    ('charm_thickness', 4.0, 'Heart charm thickness'),
    ('eyelet_thickness', 3.5, 'Charm eyelet thickness'),
    ('serration_depth', 0.8, 'Depth of the slide grooves'),
    ('readout_depth', 1.5, 'Readout window cut (through the lip into the pocket behind it)'),
]

P_GRIP_W = dict((n, v) for n, v, _ in LIVE_PARAMS)['grip_width']

# Colours from the sketch (R, G, B), by body name
CREAM = (252, 240, 185)
GRIP_PINK = (238, 112, 190)   # the grip panel; barrel and shroud match it
BODY_COLORS = {
    'Slide': (232, 72, 170),
    'Barrel': GRIP_PINK,
    'Muzzle lip': (255, 180, 206),
    'Sight bead': (250, 206, 245),
    'Heart flange': GRIP_PINK,
    'Flange inset': CREAM,
    'Frame & Grip': (250, 190, 228),
    'Grip panel': GRIP_PINK,
    'Grip pin': (190, 45, 135),
    'Trigger': (200, 70, 160),
    'ADS lever': (200, 70, 160),
    'Switch (reference)': (150, 150, 160),
    'Reload button': (225, 60, 150),
    'Infuse button': (225, 60, 150),
    'Recenter button': (250, 206, 245),
    'LED window': (255, 240, 250),
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


def slide_cavity_outline():
    """Side view of the hollow inside the slide (open at the bottom into the frame)."""
    top = SLIDE_CAVITY_TOP
    back = REAR_STRIP_W + 2.0           # stays clear of the light-pink back band
    return polygon([(slide_rear_x(-0.5) + back, -0.5), (BARREL_X0, -0.5),
                    (BARREL_X0, top), (slide_rear_x(top) + back, top)])


def slide_cavity_section():
    lo, hi = -1.0, SLIDE_CAVITY_TOP + 1.0
    return polygon([(-(slide_half_width(lo) - WALL), lo), (slide_half_width(lo) - WALL, lo),
                    (slide_half_width(hi) - WALL, hi), (-(slide_half_width(hi) - WALL), hi)])


def grip_cavity_outline():
    """Side view of the hollow inside the grip (opens up into the frame)."""
    top, bot = -FRAME_H + 4.0, GRIP_CAVITY_BOTTOM
    return polygon([(spine_rear_x(top) + 3.0, top), (PANEL_FRONT[0][0] - 5.5, top),
                    (PANEL_FRONT[2][0] - 3.0, PANEL_FRONT[2][1] - 5.0), (PANEL_FRONT[3][0] - 5.0, bot),
                    (spine_rear_x(bot) + 3.0, bot)])


def stadium(cx, cy, w, h):
    """Rounded slot w wide (front-back) and h tall (h > w)."""
    r = w / 2.0
    k = h / 2.0 - r
    return [('line', (cx + r, cy - k), (cx + r, cy + k)),
            ('arc', (cx + r, cy + k), (cx, cy + h / 2.0), (cx - r, cy + k)),
            ('line', (cx - r, cy + k), (cx - r, cy - k)),
            ('arc', (cx - r, cy - k), (cx, cy - h / 2.0), (cx + r, cy - k))]


def slide_points():
    """Slide corners: rear-bottom, front-bottom, bevel start, bevel end, rear-top."""
    L, H = SLIDE_LEN, SLIDE_H
    fx = L + SLIDE_FRONT_LEAN
    b = SLIDE_FRONT_BEVEL
    return [(0, 0), (L, 0), (fx - b * SLIDE_FRONT_LEAN / H, H - b),
            (fx - b * 1.6, H), (SLIDE_REAR_LEAN, H)]


def slide_outline():
    return polygon(slide_points())


def top_strip_outline():
    """The part of the slide outline that is light pink: a band along the
    top (TOP_STRIP_H) and down the slanted back (REAR_STRIP_W)."""
    _, f0, f1, f2, rear_top = slide_points()
    yi = SLIDE_H - TOP_STRIP_H

    def x_at(p, q, y):
        return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])
    if yi >= f1[1]:
        front = [(x_at(f1, f2, yi), yi), f2]
    else:
        front = [(x_at(f0, f1, yi), yi), f1, f2]
    # starts 1 mm below the slide so it fuses with the frame and grip back
    return polygon([(slide_rear_x(-1.0), -1.0), (REAR_STRIP_W, -1.0), (slide_rear_x(yi) + REAR_STRIP_W, yi)]
                   + front + [rear_top])


def slide_rear_x(y):
    """x of the slanted rear face at height y."""
    return SLIDE_REAR_LEAN * y / SLIDE_H


def ears_outline():
    x0, y0 = EARS_X0, SLIDE_H - 1.0   # sinks 1 mm into the slide
    return polygon([(x0, y0), (x0 + EARS_LEN, y0), (x0 + 2.0, SLIDE_H + EARS_H)])


def serration_outlines():
    """Slanted grooves on the straight upper part of the slide's sides."""
    y0, y1 = 5.0, SLIDE_H - TOP_STRIP_H - 1.0
    lean = SERRATION_LEAN * (y1 - y0) / (SLIDE_H - 10.0)
    return [polygon([(x, y0), (x + SERRATION_W, y0),
                     (x + SERRATION_W + lean, y1), (x + lean, y1)])
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


def slide_half_width(y):
    """Half the slide's width at height y (sides lean out toward the bottom)."""
    return SLIDE_TOP_W / 2.0 + (SLIDE_H - y) * math.tan(math.radians(SLIDE_SIDE_ANGLE))


SLIDE_BOTTOM_W = 2.0 * slide_half_width(0.0)


def slide_section():
    """Front-view (u, v) shape the slide and top strip are trimmed to."""
    lo, hi = -1.5, SLIDE_H + 1.0
    return polygon([(-slide_half_width(lo), lo), (slide_half_width(lo), lo),
                    (slide_half_width(hi), hi), (-slide_half_width(hi), hi)])


FRAME_W = SLIDE_BOTTOM_W      # the rectangular frame matches the slide's bottom


def barrel_half_section():
    """Half cross-section revolved around y = BORE_AXIS_Y."""
    y = BORE_AXIS_Y
    x1 = MUZZLE_X1
    bb = x1 - BORE_DEPTH
    xf = FLANGE_X + FLANGE_T
    pts = [(bb, y), (BARREL_X0, y), (BARREL_X0, y + BARREL_R), (xf, y + BARREL_R),
           (xf, y + MUZZLE_R), (x1, y + MUZZLE_R),
           (x1, y + MUZZLE_LIP_R_IN), (x1 - 1.5, y + MUZZLE_LIP_R_IN),
           (x1 - 1.5, y + MUZZLE_RING_R), (x1 - 3.0, y + MUZZLE_RING_R),
           (x1 - 3.0, y + BORE_R), (bb, y + BORE_R)]
    return polygon(pts)


def muzzle_lip_half_section():
    """Light-pink lip ring standing 1.5 mm proud of the muzzle front."""
    y, x1 = BORE_AXIS_Y, MUZZLE_X1
    return polygon([(x1 - 2.0, y + MUZZLE_LIP_R_IN), (x1 + 1.5, y + MUZZLE_LIP_R_IN),
                    (x1 + 1.5, y + MUZZLE_R + 0.5), (x1 - 2.0, y + MUZZLE_R + 0.5)])


# Front-view outlines (u = across the gun, v = height) for the flange
def flange_loops():
    return [heart(FLANGE_HEART_W, (0.0, FLANGE_HEART_CY))]


def flange_inset_loops():
    return [heart_inset(FLANGE_HEART_W, (0.0, FLANGE_HEART_CY), 0.0)]


def _sight_centre():
    cusp = FLANGE_HEART_CY + heart_shape(FLANGE_HEART_W)[1]['cusp_y']
    return cusp, (0.0, cusp + SIGHT_LIFT)


def front_sight_loops():
    """Two horns: a ring open at the top, with rounded tips."""
    _, c = _sight_centre()
    ro, ri = SIGHT_R_OUT, SIGHT_R_IN
    rr = (ro - ri) / 2.0

    def at(r, deg):
        a = math.radians(deg)
        return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
    a_r, a_l = 90.0 - SIGHT_GAP_DEG, 90.0 + SIGHT_GAP_DEG     # right / left tip angles
    m_r, m_l = at((ro + ri) / 2.0, a_r), at((ro + ri) / 2.0, a_l)
    cap_r = (m_r[0] - rr * math.sin(math.radians(a_r)), m_r[1] + rr * math.cos(math.radians(a_r)))
    cap_l = (m_l[0] + rr * math.sin(math.radians(a_l)), m_l[1] - rr * math.cos(math.radians(a_l)))
    return [[
        ('arc', at(ro, a_l), at(ro, 270.0), at(ro, a_r)),
        ('arc', at(ro, a_r), cap_r, at(ri, a_r)),
        ('arc', at(ri, a_r), at(ri, 270.0), at(ri, a_l)),
        ('arc', at(ri, a_l), cap_l, at(ro, a_l)),
    ]]


def sight_bead_loops():
    cusp, _ = _sight_centre()
    return [[('circle', (0.0, cusp + 1.5), SIGHT_BEAD_R)]]


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
    """Whole grip (back piece + panel) as one outline. The back runs up to
    y = 0 to meet the light-pink strip on the slide."""
    top = 0.0
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
    # Under the guard, a curved web sweeps down into the front of the grip so
    # the guard flows into the grip panel instead of meeting it at a corner.
    web0 = (GUARD_IN_REAR_X + 6.0, by)
    web1 = (PANEL_FRONT[2][0] + 0.5, by - GUARD_WEB_DROP)
    web_mid = (web0[0] - 0.71 * (web0[0] - web1[0]), web1[1] + 0.71 * (web0[1] - web1[1]))
    outer = [
        ('line', (rear, -h + 2), (fx, -h + 2)),
        ('arc', (fx, -h + 2), (fx + 8, (-h + by) / 2 + 2), (fx - 6, by)),
        ('line', (fx - 6, by), web0),
        ('arc', web0, web_mid, web1),
        ('line', web1, (rear, web1[1])),
        ('line', (rear, web1[1]), (rear, -h + 2)),
    ]
    ir, ifx, iby = GUARD_IN_REAR_X, GUARD_IN_FRONT_X, GUARD_IN_BOTTOM_Y
    inner = [
        ('line', (ir, -h), (ifx, -h)),
        ('arc', (ifx, -h), (ifx + 6, (-h + iby) / 2 + 1), (ifx - 6, iby)),
        ('line', (ifx - 6, iby), (ir - 1, iby)),
        ('line', (ir - 1, iby), (ir, -h)),
    ]
    return [outer, inner]


def trigger_loops():
    """Trigger pieces (joined into one part): a boss round the pivot, an arm
    down through the frame, the curved finger blade and the nub at the back
    that presses the switch."""
    px, py = TRIGGER_PIVOT
    return [
        [('circle', (px, py), 3.8)],
        polygon([(px - 3.5, -14.0), (px + 3.5, -14.0), (px + 3.5, py), (px - 3.5, py)]),
        [('line', (40.5, -13.0), (49.0, -13.0)),
         ('arc', (49.0, -13.0), (46.0, -17.0), (49.0, -21.5)),
         ('line', (49.0, -21.5), (46.5, -23.0)),
         ('arc', (46.5, -23.0), (41.5, -18.0), (40.5, -13.0))],
        polygon([(TRIGGER_SWITCH[1] + 2.5, -17.5), (px - 2.0, -17.5), (px - 2.0, -14.5),
                 (TRIGGER_SWITCH[1] + 2.5, -14.5)]),
    ]


def ads_loops():
    """ADS lever pieces: a boss round its pivot, a block through the slot in
    the grip front, and the finger pad in the guard below the trigger."""
    px, py = ADS_PIVOT
    sw = ADS_SWITCH
    return [
        [('circle', (px, py), 3.5)],
        polygon([(sw[1] + 2.0, sw[2] + 1.5), (px + 5.0, sw[2] + 1.5), (px + 5.0, py), (sw[1] + 2.0, py)]),
        polygon([(px + 4.0, sw[2] + 1.0), (px + 11.5, sw[2] + 1.0), (px + 11.5, py - 1.5), (px + 4.0, py - 1.5)]),
    ]


def trigger_outline():
    """Just the finger blade (used by the preview)."""
    return trigger_loops()[2]


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


def heart_dome_centre(width, center, tilt_deg, scale=1.0):
    """Where the puffy heart's dome peaks (side view): between the lobes and
    the tip, a bit toward the lobes."""
    info = heart_shape(width)[1]
    p = _rot((0.0, -0.35 * info['h'] * scale), tilt_deg)
    return (center[0] + p[0], center[1] + p[1])


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


def face_sketch(comp, face):
    """Sketch on a body face WITHOUT copying the face's outline into it.
    (A plain sketches.add(face) projects the face's edges, and the biggest
    profile is then the whole face, so a cut would remove the whole side.)"""
    try:
        return comp.sketches.addWithoutEdges(face)
    except Exception:
        sk = comp.sketches.add(face)
        for i in range(sk.sketchCurves.count - 1, -1, -1):   # drop projected edges
            c = sk.sketchCurves.item(i)
            if c.isReference:
                c.deleteMe()
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
    """Join tools into target. If joining them all at once fails, join them
    one by one and report any that would not join."""
    if not tools:
        return

    def join(items):
        coll = adsk.core.ObjectCollection.create()
        for t in items:
            coll.add(t)
        inp = comp.features.combineFeatures.createInput(target, coll)
        inp.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        inp.isKeepToolBodies = False
        comp.features.combineFeatures.add(inp)
    try:
        join(tools)
    except Exception:
        for t in tools:
            name = t.name
            try:
                join([t])
            except Exception:
                _skipped.append('{}: could not join "{}"'.format(comp.name, name))


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
    slide = extrude_sym(comp, pick_profile(sk), SLIDE_BOTTOM_W + 10.0, NEW, name='Slide').bodies.item(0)
    trim_to_section(comp, slide, slide_section(), 'Slide')
    fillet(comp, body_named(comp, 'Slide'), FILLET_SLIDE, 'Slide')
    # The top/back band is light pink and belongs to the Frame & Grip piece
    sk = side_sketch(comp, 'Top strip cut', [top_strip_outline()])
    extrude_sym(comp, pick_profile(sk), SLIDE_BOTTOM_W + 20.0, CUT, participants=[body_named(comp, 'Slide')])
    slide = body_named(comp, 'Slide')

    # Slanted grooves, sketched right on each leaning side face
    for side, label in ((1, 'left'), (-1, 'right')):
        face = side_face(slide, side, 0.0, SLIDE_H)
        if face is None:
            _skipped.append('Slide: {} grooves skipped (side face not found)'.format(label))
            continue
        sk = face_sketch(comp, face)
        sk.name = 'Grooves ({})'.format(label)
        draw_loops(sk, serration_outlines(), lambda p, s=side: (p[0], p[1], s * slide_half_width(p[1])))
        try:
            extrude_sym(comp, all_profiles(sk), 'serration_depth * 2', CUT, participants=[slide])
        except Exception:
            _skipped.append('Slide: {} grooves skipped'.format(label))

    # Hollow inside (room for the IMU, wiring and LED stick)
    try:
        sk = side_sketch(comp, 'Slide hollow', [slide_cavity_outline()])
        cav = extrude_sym(comp, pick_profile(sk), SLIDE_BOTTOM_W + 10.0, NEW, name='Slide hollow').bodies.item(0)
        trim_to_section(comp, cav, slide_cavity_section(), 'Slide hollow')
        combine_cut(comp, body_named(comp, 'Slide'), [body_named(comp, 'Slide hollow')])
    except Exception:
        _skipped.append('Slide: could not hollow it out')
    cut_top_openings(comp, body_named(comp, 'Slide'))
    cut_side_hole(comp, body_named(comp, 'Slide'), INFUSE_POS, slide_half_width(INFUSE_POS[1]), 'Infuse hole')
    slide_mounts(comp)
    add_posts(comp, 'Slide')
    halves = split_left_right(comp, 'Slide')
    if halves:
        fastener_holes(comp, 'Slide', *halves)
    return comp


def wall_z(host, pos):
    """(outer face, inner face) of the left wall at a screw post, in z mm."""
    if host == 'Slide':
        return slide_half_width(pos[1]), slide_half_width(pos[1]) - WALL
    if host == 'Frame & Grip' and pos[1] > -FRAME_H:
        return FRAME_W / 2.0, FRAME_W / 2.0 - WALL
    return P_GRIP_W / 2.0, GRIP_CAVITY_HALF_W


def active_posts():
    """Fastener positions for the chosen FASTENER."""
    return STANDOFF_POSTS if FASTENER == 'standoff' else SCREW_POSTS


def active_post_r():
    return STANDOFF_POST_R if FASTENER == 'standoff' else POST_R


def add_posts(comp, host):
    """Fastener posts spanning the hollow from wall to wall, joined to host."""
    tools = []
    for i, pos in enumerate(active_posts().get(host, [])):
        _, inner = wall_z(host, pos)
        sk = side_sketch(comp, '{} post {}'.format(host, i + 1), [[('circle', pos, active_post_r())]])
        tools.append(extrude_sym(comp, pick_profile(sk), 2.0 * (inner + 0.8), NEW,
                                 name='Screw post').bodies.item(0))
    combine_join(comp, body_named(comp, host), tools)


def fastener_holes(comp, host, left, right):
    if FASTENER == 'standoff':
        standoff_holes(comp, host)
    else:
        screw_holes(comp, host, left, right)


def standoff_holes(comp, host):
    """Hex pocket for the standoff body in the left half; a hole for its
    thread and a nut-driver hole in the right half (the nut bears on the
    bottom of that hole and pulls the halves together)."""
    r_hex = (STANDOFF_HEX_AF + 0.2) / math.sqrt(3.0)
    nut_seat = STUD_LEN - NUT_T - 0.2           # depth of the plastic under the nut
    for i, pos in enumerate(active_posts().get(host, [])):
        outer, _ = wall_z(host, pos)
        hexagon = polygon([(pos[0] + r_hex * math.cos(math.radians(60 * k)),
                            pos[1] + r_hex * math.sin(math.radians(60 * k))) for k in range(6)])
        try:
            sk = side_sketch(comp, '{} standoff pocket {}'.format(host, i + 1), [hexagon],
                             plane=xy_plane(comp, STANDOFF_LEN / 2.0))
            extrude_sym(comp, pick_profile(sk), STANDOFF_LEN, CUT, participants=[body_named(comp, host + ' L')])
            sk = side_sketch(comp, '{} stud hole {}'.format(host, i + 1), [[('circle', pos, SCREW_CLEAR_R)]],
                             plane=xy_plane(comp, -(outer + 1.0) / 2.0))
            extrude_sym(comp, pick_profile(sk), outer + 1.0, CUT, participants=[body_named(comp, host + ' R')])
            z_far, z_near = -(outer + 1.0), -nut_seat
            sk = side_sketch(comp, '{} nut hole {}'.format(host, i + 1), [[('circle', pos, NUT_DRIVER_R)]],
                             plane=xy_plane(comp, (z_far + z_near) / 2.0))
            extrude_sym(comp, pick_profile(sk), z_near - z_far, CUT, participants=[body_named(comp, host + ' R')])
        except Exception:
            _skipped.append('{}: standoff {} holes skipped'.format(host, i + 1))


def split_left_right(comp, name):
    """Split a body down the middle (z = 0) into '<name> L' and '<name> R'."""
    others = set(b.entityToken for b in bodies(comp) if b.name != name)
    try:
        splits = comp.features.splitBodyFeatures
        splits.add(splits.createInput(body_named(comp, name), comp.xYConstructionPlane, True))
    except Exception:
        _skipped.append('{}: could not split into left and right halves'.format(name))
        return None
    left = right = None
    # the halves are the solids that weren't there before (Fusion names the
    # new one "Body..."), so find them by elimination
    for b in bodies(comp):
        if b.entityToken in others or not b.isSolid:
            continue
        bb = b.boundingBox
        if bb.maxPoint.z + bb.minPoint.z > 0:
            b.name, left = name + ' L', b
        else:
            b.name, right = name + ' R', b
    return (left, right) if left and right else None


def screw_holes(comp, host, left, right):
    """Insert holes in the left half; clearance holes with a recess for the
    screw head in the right half (screws go in from the right)."""
    for i, pos in enumerate(SCREW_POSTS.get(host, [])):
        outer, _ = wall_z(host, pos)
        try:
            sk = side_sketch(comp, '{} insert {}'.format(host, i + 1), [[('circle', pos, INSERT_R)]],
                             plane=xy_plane(comp, INSERT_DEPTH / 2.0))
            extrude_sym(comp, pick_profile(sk), INSERT_DEPTH, CUT, participants=[body_named(comp, host + ' L')])
            sk = side_sketch(comp, '{} screw hole {}'.format(host, i + 1), [[('circle', pos, SCREW_CLEAR_R)]],
                             plane=xy_plane(comp, -(outer + 1.0) / 2.0))
            extrude_sym(comp, pick_profile(sk), outer + 1.0, CUT, participants=[body_named(comp, host + ' R')])
            z_far, z_near = -(outer + 1.0), -(outer - HEAD_DEPTH)
            sk = side_sketch(comp, '{} screw head {}'.format(host, i + 1), [[('circle', pos, HEAD_R)]],
                             plane=xy_plane(comp, (z_far + z_near) / 2.0))
            extrude_sym(comp, pick_profile(sk), z_near - z_far, CUT, participants=[body_named(comp, host + ' R')])
        except Exception:
            _skipped.append('{}: screw {} holes skipped'.format(host, i + 1))


def combine_cut(comp, target, tools, keep=False):
    coll = adsk.core.ObjectCollection.create()
    for t in tools:
        coll.add(t)
    inp = comp.features.combineFeatures.createInput(target, coll)
    inp.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    inp.isKeepToolBodies = keep
    comp.features.combineFeatures.add(inp)


def xy_plane(comp, z):
    if abs(z) < 1e-9:
        return comp.xYConstructionPlane
    return offset_plane(comp, comp.xYConstructionPlane, z, 'z', z)


def cut_top_openings(comp, body):
    """The LED window and the reload button slot through the top."""
    y0, y1 = SLIDE_CAVITY_TOP - 0.5, SLIDE_H + 1.0
    for name, x0, x1, w in (('LED window opening', LED_WINDOW_X[0], LED_WINDOW_X[1], LED_WINDOW_W),
                            ('Reload slot', BUTTON_X0 - CLEAR, BUTTON_X1 + CLEAR,
                             RELOAD_W + 2 * CLEAR)):
        try:
            sk = side_sketch(comp, name, [polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])])
            extrude_sym(comp, pick_profile(sk), w, CUT, participants=[body])
        except Exception:
            _skipped.append('{}: {} skipped'.format(comp.name, name))


def cut_side_hole(comp, bodies_to_cut, pos, z_outer, name, r=None):
    """Round hole through the LEFT wall (+Z) at side-view position pos."""
    r = r or (SIDE_BUTTON_D / 2.0 + CLEAR)
    if not isinstance(bodies_to_cut, list):
        bodies_to_cut = [bodies_to_cut]
    try:
        sk = side_sketch(comp, name, [[('circle', pos, r)]], plane=xy_plane(comp, z_outer - WALL / 2.0))
        extrude_sym(comp, pick_profile(sk), WALL + 4.0, CUT, participants=bodies_to_cut)
    except Exception:
        _skipped.append('{}: {} skipped'.format(comp.name, name))


def trim_to_section(comp, body, section_loop, label):
    """Intersect a body with a long prism of the given front-view shape, so
    its cross-section (seen from the front) becomes that shape."""
    sk = front_sketch(comp, '{} cross-section'.format(label), [section_loop], 60.0)
    try:
        extrude_sym(comp, pick_profile(sk), 400.0, adsk.fusion.FeatureOperations.IntersectFeatureOperation,
                    participants=[body])
    except Exception:
        _skipped.append('{}: could not shape its cross-section, left straight-sided'.format(label))


def side_face(body, side, y_lo, y_hi):
    """The biggest flat face on the given side (+1 = +Z = left, -1 = right)
    that leans sideways, with its centre between y_lo and y_hi (outline mm)."""
    best, best_area = None, 0.0
    for i in range(body.faces.count):
        f = body.faces.item(i)
        plane = adsk.core.Plane.cast(f.geometry)
        if not plane:
            continue
        n = plane.normal
        p = f.pointOnFace
        if abs(n.z) < 0.3 or abs(n.x) > 0.3 or p.z * side <= 0:
            continue
        if not (y_lo <= p.y * 10 <= y_hi):
            continue
        if f.area > best_area:
            best, best_area = f, f.area
    return best


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
    sk = front_sketch(comp, 'Front sight horns', front_sight_loops(), mid)
    flange = body_named(comp, 'Heart flange')
    extrude_sym(comp, pick_profile(sk), 'sight_thickness', JOIN, participants=[flange])
    sk = front_sketch(comp, 'Front sight bead', sight_bead_loops(), mid)
    extrude_sym(comp, pick_profile(sk), 'sight_thickness + 1 mm', NEW, name='Sight bead')
    front = FLANGE_X + FLANGE_T
    sk = front_sketch(comp, 'Flange inset', flange_inset_loops(), front)
    extrude_sym(comp, pick_profile(sk), 'inset_proud * 2', NEW, name='Flange inset')
    fillet(comp, body_named(comp, 'Flange inset'), 0.6, 'Flange inset', edge_filter=flat_in('x'))
    return comp


def build_frame(root):
    comp = new_component(root, 'Frame & Grip')

    sk = side_sketch(comp, 'Frame profile', [frame_outline()])
    frame = extrude_sym(comp, pick_profile(sk), FRAME_W, NEW, name='Frame').bodies.item(0)
    fillet(comp, frame, FILLET_FRAME, 'Frame')

    # Readout window recess on the left side of the frame
    frame = body_named(comp, 'Frame')
    band = side_face(frame, 1, -FRAME_H, 0.0)
    if band is None:
        _skipped.append('Frame: readout window skipped (side face not found)')
    else:
        sk = face_sketch(comp, band)
        sk.name = 'Readout window'
        draw_loops(sk, [readout_outline()], lambda p: (p[0], p[1], FRAME_W / 2.0))
        extrude_sym(comp, pick_profile(sk), 'readout_depth * 2', CUT, participants=[frame])

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

    # Light-pink strip on the top and back of the slide, with the cat ears
    sk = side_sketch(comp, 'Top strip', [top_strip_outline()])
    strip = extrude_sym(comp, pick_profile(sk), SLIDE_BOTTOM_W + 10.0, NEW, name='Top strip').bodies.item(0)
    trim_to_section(comp, strip, slide_section(), 'Top strip')
    fillet(comp, body_named(comp, 'Top strip'), FILLET_SLIDE, 'Top strip',
           edge_filter=lambda e: e.boundingBox.minPoint.y * 10 > SLIDE_H - TOP_STRIP_H + 0.5)
    sk = side_sketch(comp, 'Ears profile', [ears_outline()])
    ears = extrude_sym(comp, pick_profile(sk), SLIDE_TOP_W - 4.0, NEW, name='Ears').bodies.item(0)
    sk = front_sketch(comp, 'Ears notch', [polygon([
        (-EARS_GAP / 2, SLIDE_H + 0.5), (EARS_GAP / 2, SLIDE_H + 0.5),
        (EARS_GAP / 2, SLIDE_H + EARS_H + 5), (-EARS_GAP / 2, SLIDE_H + EARS_H + 5)])],
        EARS_X0 + EARS_LEN / 2)
    extrude_sym(comp, pick_profile(sk), EARS_LEN * 3, CUT, participants=[ears])
    fillet(comp, body_named(comp, 'Ears'), 0.6, 'Ears',
           edge_filter=lambda e: e.boundingBox.minPoint.y * 10 > SLIDE_H + 0.2)

    # Grip loop (the hook from the heart into the grip back), same light pink
    if INCLUDE_GRIP_LOOP:
        sk = side_sketch(comp, 'Grip loop profile', [grip_loop_outline()])
        extrude_sym(comp, pick_profile(sk), 'loop_width', NEW, name='Grip loop')
        fillet(comp, body_named(comp, 'Grip loop'), 2.5, 'Grip loop')

    # Trigger guard: same dark pink as the grip panel and one piece with it
    sk = side_sketch(comp, 'Trigger guard profile', guard_loops())
    guard = extrude_sym(comp, pick_profile(sk, loops=2), 'guard_width', NEW, name='Guard').bodies.item(0)
    fillet(comp, guard, FILLET_GUARD, 'Trigger guard')
    combine_join(comp, body_named(comp, 'Grip panel'), [body_named(comp, 'Guard')])

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
    hollow_frame_and_grip(comp)
    lever_mounts(comp)
    frame_mounts(comp)
    for host in ('Frame & Grip', 'Grip panel'):
        add_posts(comp, host)
        halves = split_left_right(comp, host)
        if halves:
            fastener_holes(comp, host, *halves)
    return comp


def join_mounts(comp, host, boxes):
    """Make each (name, x0, x1, y0, y1, z0, z1) box and join them to host."""
    try:
        tools = [box_tool(comp, *b) for b in boxes]
        combine_join(comp, body_named(comp, host), tools)
    except Exception:
        _skipped.append('{}: mounts skipped'.format(host))


def slide_mounts(comp):
    """Inside the slide: a shelf under the reload switch, a column under the
    infuse switch (right half), and two ledges holding the LED stick."""
    rs = 6.5                                    # half of a 12 mm switch + margin
    rx = (BUTTON_X0 + BUTTON_X1) / 2.0
    shelf_top = SLIDE_CAVITY_TOP - 1.0 - TACT_H   # reload switch plunger meets the flange
    w_shelf = slide_half_width(shelf_top) - WALL + 0.5
    ix, iy = INFUSE_POS
    x0, x1 = LED_WINDOW_X
    led_bottom = SLIDE_H - TOP_STRIP_H - 3.2    # the stick sits right under the window
    boxes = [
        ('Reload switch shelf', rx - rs, rx + rs, shelf_top - 2.0, shelf_top, -w_shelf, w_shelf),
        ('Infuse switch column', ix - rs, ix + rs, iy - rs, iy + rs,
         -(slide_half_width(iy + rs) - WALL) - 0.5, TACT_SEAT),
    ]
    for side, label in ((1, 'left'), (-1, 'right')):
        z_in, z_out = sorted((side * 4.0, side * 7.5))
        boxes.append(('LED ledge ' + label, x0, x1, led_bottom - 1.5, led_bottom, z_in, z_out))
        z_in, z_out = sorted((side * 5.6, side * 7.5))
        boxes.append(('LED hanger ' + label, x0, x1, led_bottom - 1.5, SLIDE_CAVITY_TOP + 0.3, z_in, z_out))
    join_mounts(comp, 'Slide', boxes)


def frame_mounts(comp):
    """Inside the frame and grip: ledges under the two microswitches, a
    column under the recenter switch (right half), rails holding the top of
    the Nano, and a cradle for the IMU on the frame floor."""
    rs = 6.5
    cx, cy = RECENTER_POS
    bl, bw, bt = BOARD_SIZE
    top = GRIP_BASE_Y + BOARD_FLOOR + bl
    floor = -FRAME_H + 2.0
    il, iw = IMU_SIZE
    panel_boxes = [
        ('Trigger switch ledge', TRIGGER_SWITCH[0] - 4.0, TRIGGER_SWITCH[1], TRIGGER_SWITCH[2] - 2.0,
         TRIGGER_SWITCH[2], -SWITCH_HALF_LEN, SWITCH_HALF_LEN),
        ('ADS switch ledge', ADS_SWITCH[0] - 4.0, ADS_SWITCH[1], ADS_SWITCH[2] - 2.0,
         ADS_SWITCH[2], -SWITCH_HALF_LEN, SWITCH_HALF_LEN),
    ]
    frame_boxes = [
        ('Recenter switch column', cx - rs, cx + rs, cy - rs, cy + rs, -GRIP_CAVITY_HALF_W - 0.5, TACT_SEAT),
        ('IMU cradle end front', IMU_X + il / 2 + 0.3, IMU_X + il / 2 + 1.8, floor, floor + 2.0, -iw / 2 - 2, iw / 2 + 2),
        ('IMU cradle end back', IMU_X - il / 2 - 1.8, IMU_X - il / 2 - 0.3, floor, floor + 2.0, -iw / 2 - 2, iw / 2 + 2),
    ]
    for side, label in ((1, 'left'), (-1, 'right')):
        z_in, z_out = sorted((side * (bw / 2.0 - 1.3), side * (GRIP_CAVITY_HALF_W + 0.5)))
        frame_boxes.append(('Nano rail ' + label, BOARD_X - 6.0, BOARD_X - bt / 2.0 - 0.25, top - 2.7, top,
                            z_in, z_out))
        frame_boxes.append(('Nano rail ' + label + ' 2', BOARD_X + bt / 2.0 + 0.25, BOARD_X + 6.0, top - 2.7, top,
                            z_in, z_out))
        z_in, z_out = sorted((side * (iw / 2 + 0.3), side * (iw / 2 + 2.0)))
        frame_boxes.append(('IMU cradle side ' + label, IMU_X - il / 2, IMU_X + il / 2, floor, floor + 2.0,
                            z_in, z_out))
    join_mounts(comp, 'Grip panel', panel_boxes)
    join_mounts(comp, 'Frame & Grip', frame_boxes)


def lever_mounts(comp):
    """Slots for the trigger and ADS lever, their pin holes, and stops behind
    the two microswitches."""
    def frame():
        return body_named(comp, 'Frame & Grip')

    def panel():
        return body_named(comp, 'Grip panel')
    tw = 7.0 + 2 * CLEAR                     # trigger_width + clearance
    px, py = TRIGGER_PIVOT
    ax_, ay = ADS_PIVOT
    cuts = [
        ('Trigger arm slot', polygon([(px - 4.5, -FRAME_H - 1.5), (px + 5.5, -FRAME_H - 1.5),
                                      (px + 5.5, -1.5), (px - 4.5, -1.5)]), tw, 'both'),   # room for it to swing
        ('Trigger nub slot', polygon([(TRIGGER_SWITCH[1], -18.5), (px - 4.0, -18.5),
                                      (px - 4.0, -13.5), (TRIGGER_SWITCH[1], -13.5)]), 5.0 + 2 * CLEAR, 'panel'),
        ('ADS lever slot', polygon([(ADS_SWITCH[1] + 0.5, ADS_SWITCH[2]), (ax_ + 6.0, ADS_SWITCH[2]),
                                    (ax_ + 6.0, ay + 4.0), (ADS_SWITCH[1] + 0.5, ay + 4.0)]), tw, 'panel'),
        ('Trigger pin hole', [('circle', TRIGGER_PIVOT, PIVOT_PIN_R)], 60.0, 'both'),
        ('ADS pin hole', [('circle', ADS_PIVOT, PIVOT_PIN_R)], 60.0, 'both'),
    ]
    for name, loop, width, which in cuts:
        try:
            sk = side_sketch(comp, name, [loop])
            targets = [panel()] if which == 'panel' else [frame(), panel()]
            extrude_sym(comp, pick_profile(sk), width, CUT, participants=targets)
        except Exception:
            _skipped.append('Frame & Grip: {} skipped'.format(name))
    stops = []
    for label, (x0, x1, y0, y1) in (('Trigger switch stop', TRIGGER_SWITCH), ('ADS switch stop', ADS_SWITCH)):
        sk = side_sketch(comp, label, [polygon([(x0 - 4.0, y0), (x0, y0), (x0, y1), (x0 - 4.0, y1)])])
        stops.append(extrude_sym(comp, pick_profile(sk), 2.0 * GRIP_CAVITY_HALF_W + 1.0, NEW,
                                 name='Switch stop').bodies.item(0))
    combine_join(comp, panel(), stops)


def box_tool(comp, name, x0, x1, y0, y1, z0, z1):
    """A box from (x0, y0, z0) to (x1, y1, z1) as a new body, for cutting."""
    sk = side_sketch(comp, name, [polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])],
                     plane=xy_plane(comp, (z0 + z1) / 2.0))
    return extrude_sym(comp, pick_profile(sk), z1 - z0, NEW, name=name).bodies.item(0)


def hollow_frame_and_grip(comp):
    """Hollow the grip (for the board) and the frame (joining the slide's and
    grip's hollows), add the readout pocket, and cut the top openings, the
    recenter hole and the USB-C port."""
    frame, panel = body_named(comp, 'Frame & Grip'), body_named(comp, 'Grip panel')
    try:
        sk = side_sketch(comp, 'Grip hollow', [grip_cavity_outline()])
        extrude_sym(comp, pick_profile(sk), 2.0 * GRIP_CAVITY_HALF_W, NEW, name='Grip hollow')
        combine_cut(comp, panel, [body_named(comp, 'Grip hollow')], keep=True)
        combine_cut(comp, body_named(comp, 'Frame & Grip'), [body_named(comp, 'Grip hollow')])
    except Exception:
        _skipped.append('Frame & Grip: could not hollow out the grip')

    # Frame hollow (open up into the slide and down into the grip) and the
    # readout pocket (behind the window, under a thin lip)
    outer = FRAME_W / 2.0
    hw = outer - WALL
    z_lip = outer - READOUT_LIP
    tools = [
        box_tool(comp, 'Frame hollow', FRAME_CAVITY_X[0], FRAME_CAVITY_X[1], -FRAME_H + 2.0, 0.5, -hw, hw),
        box_tool(comp, 'Readout pocket', READOUT_X0 - 1.0, READOUT_X1 + 1.0,
                 READOUT_Y0 - 0.5, READOUT_Y1 + 0.5, z_lip - READOUT_POCKET_DEPTH, z_lip),
    ]
    try:
        combine_cut(comp, body_named(comp, 'Frame & Grip'), tools)
    except Exception:
        _skipped.append('Frame & Grip: could not hollow out the frame')
    frame, panel = body_named(comp, 'Frame & Grip'), body_named(comp, 'Grip panel')
    cut_top_openings(comp, frame)
    cut_side_hole(comp, [frame, panel], RECENTER_POS, P_GRIP_W / 2.0, 'Recenter hole')

    # Nano ESP32: pocket in the base for its USB end, a wider space above it
    # for the wires on its pins, and the USB-C port through the bottom
    _, bw, bt = BOARD_SIZE
    y_board = GRIP_BASE_Y + BOARD_FLOOR
    try:
        tools = [box_tool(comp, 'Board pocket', BOARD_X - bt / 2.0 - 0.5, BOARD_X + bt / 2.0 + 0.5,
                          y_board, y_board + 4.0, -bw / 2.0 - 0.3, bw / 2.0 + 0.3),
                 box_tool(comp, 'Board wiring space', BOARD_X - 7.0, BOARD_X + 7.0,
                          y_board + 4.0, GRIP_CAVITY_BOTTOM + 1.0, -bw / 2.0 - 1.0, bw / 2.0 + 1.0)]
        combine_cut(comp, body_named(comp, 'Grip panel'), tools, keep=True)
        combine_cut(comp, body_named(comp, 'Frame & Grip'),
                    [body_named(comp, 'Board pocket'), body_named(comp, 'Board wiring space')])
    except Exception:
        _skipped.append('Frame & Grip: Nano pocket skipped')
    try:
        pl = offset_plane(comp, comp.xZConstructionPlane, (GRIP_BASE_Y + y_board) / 2.0, 'y',
                          (GRIP_BASE_Y + y_board) / 2.0)
        sk = comp.sketches.add(pl)
        sk.name = 'USB-C port'
        yp = (GRIP_BASE_Y + y_board) / 2.0
        draw_loops(sk, [stadium(BOARD_X, 0.0, USB_HOLE[0], USB_HOLE[1])], lambda p: (p[0], yp, p[1]))
        extrude_sym(comp, pick_profile(sk), BOARD_FLOOR + 4.0, CUT,
                    participants=[body_named(comp, 'Frame & Grip'), body_named(comp, 'Grip panel')])
    except Exception:
        _skipped.append('Frame & Grip: USB-C port skipped')


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


def build_lever(comp, name, loops, pivot):
    """Extrude each piece, join them, and drill the pivot hole."""
    made = []
    for i, loop in enumerate(loops):
        sk = side_sketch(comp, '{} piece {}'.format(name, i + 1), [loop])
        made.append(extrude_sym(comp, pick_profile(sk), 'trigger_width', NEW,
                                name='{} piece {}'.format(name, i + 1)).bodies.item(0))
    combine_join(comp, made[0], made[1:])
    body = body_named(comp, '{} piece 1'.format(name))
    body.name = name
    sk = side_sketch(comp, '{} pivot hole'.format(name), [[('circle', pivot, PIVOT_PIN_R + 0.15)]])
    extrude_sym(comp, pick_profile(sk), 20.0, CUT, participants=[body])
    fillet(comp, body_named(comp, name), 0.6, name, edge_filter=flat_in('z'))
    return body_named(comp, name)


def build_trigger(root):
    comp = new_component(root, 'Trigger')
    build_lever(comp, 'Trigger', trigger_loops(), TRIGGER_PIVOT)
    return comp


def build_ads(root):
    comp = new_component(root, 'ADS Lever')
    build_lever(comp, 'ADS lever', ads_loops(), ADS_PIVOT)
    return comp


def build_switch_refs(root):
    """Grey stand-ins for the two lever microswitches, to check the fit.
    Not printed."""
    comp = new_component(root, 'Switches (reference)')
    for label, (x0, x1, y0, y1) in (('Trigger switch', TRIGGER_SWITCH), ('ADS switch', ADS_SWITCH)):
        sk = side_sketch(comp, label, [polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])])
        extrude_sym(comp, pick_profile(sk), 2.0 * SWITCH_HALF_LEN, NEW, name='Switch (reference)')
    return comp


def build_button(root):
    """Reload button: the pill on top, with a stem down through its slot and
    a flange underneath that stops it falling out. The 12 mm tactile switch
    sits under the flange."""
    comp = new_component(root, 'Reload Button')
    sk = side_sketch(comp, 'Button profile', [button_outline()])
    body = extrude_sym(comp, pick_profile(sk), RELOAD_W, NEW, name='Reload button').bodies.item(0)
    fillet(comp, body, 2.0, 'Reload button', edge_filter=flat_in('z'))
    y_in = SLIDE_CAVITY_TOP
    sk = side_sketch(comp, 'Reload stem', [polygon([(BUTTON_X0, y_in), (BUTTON_X1, y_in),
                                                    (BUTTON_X1, SLIDE_H), (BUTTON_X0, SLIDE_H)])])
    extrude_sym(comp, pick_profile(sk), RELOAD_W, JOIN, participants=[body_named(comp, 'Reload button')])
    sk = side_sketch(comp, 'Reload flange', [polygon([(BUTTON_X0 - 1.5, y_in - 1.0), (BUTTON_X1 + 1.5, y_in - 1.0),
                                                      (BUTTON_X1 + 1.5, y_in), (BUTTON_X0 - 1.5, y_in)])])
    extrude_sym(comp, pick_profile(sk), RELOAD_W + 3.0, JOIN, participants=[body_named(comp, 'Reload button')])
    return comp


def build_side_button(root, comp_name, body_name, pos, z_outer, z_in):
    """Round button cap through the left wall (outer face at z_outer, inner
    face at z_in), with a flange 1 mm clear of the inner face and a stem
    reaching in to the tactile switch's plunger."""
    comp = new_component(root, comp_name)
    r = SIDE_BUTTON_D / 2.0
    z0, z1 = z_in - 2.0, z_outer + SIDE_BUTTON_PROUD
    sk = side_sketch(comp, body_name + ' cap', [[('circle', pos, r)]], plane=xy_plane(comp, (z0 + z1) / 2.0))
    extrude_sym(comp, pick_profile(sk), z1 - z0, NEW, name=body_name)
    sk = side_sketch(comp, body_name + ' flange', [[('circle', pos, r + 1.25)]],
                     plane=xy_plane(comp, z_in - 1.5))
    extrude_sym(comp, pick_profile(sk), 1.0, JOIN, participants=[body_named(comp, body_name)])
    plunger_top = TACT_SEAT + TACT_H
    if plunger_top < z0:
        sk = side_sketch(comp, body_name + ' stem', [[('circle', pos, 2.5)]],
                         plane=xy_plane(comp, (plunger_top + z0 + 0.5) / 2.0))
        extrude_sym(comp, pick_profile(sk), z0 + 0.5 - plunger_top, JOIN,
                    participants=[body_named(comp, body_name)])
    fillet(comp, body_named(comp, body_name), 1.0, body_name,
           edge_filter=lambda e: flat_in('z')(e) and e.boundingBox.minPoint.z * 10 > z_outer)
    return comp


def build_infuse(root):
    # the slide's walls lean in toward the top, so measure the inner face
    # at the top of the button
    top_y = INFUSE_POS[1] + SIDE_BUTTON_D / 2.0 + 1.25
    return build_side_button(root, 'Infuse Button', 'Infuse button', INFUSE_POS,
                             slide_half_width(INFUSE_POS[1]), slide_half_width(top_y) - WALL)


def build_recenter(root):
    return build_side_button(root, 'Recenter Button', 'Recenter button', RECENTER_POS, P_GRIP_W / 2.0,
                             GRIP_CAVITY_HALF_W)


def build_led_window(root):
    """Translucent window over the LED stick, flush with the top."""
    comp = new_component(root, 'LED Window')
    x0, x1 = LED_WINDOW_X[0] + CLEAR, LED_WINDOW_X[1] - CLEAR
    sk = side_sketch(comp, 'LED window', [polygon([(x0, SLIDE_H - TOP_STRIP_H), (x1, SLIDE_H - TOP_STRIP_H),
                                                   (x1, SLIDE_H), (x0, SLIDE_H)])])
    body = extrude_sym(comp, pick_profile(sk), LED_WINDOW_W - 2 * CLEAR, NEW, name='LED window').bodies.item(0)
    fillet(comp, body, 0.8, 'LED window', edge_filter=lambda e: e.boundingBox.minPoint.y * 10 > SLIDE_H - 0.1)
    return comp


def build_rear_cap(root):
    """Puffy 3D heart: the heart outline swells out into a smooth dome on
    each side. The cream centre is a slightly smaller, slightly taller dome
    that bulges out through the middle of each side."""
    comp = new_component(root, 'Rear Cap (Heart)')
    build_dome_heart(comp, 'Heart cap', cap_outline(),
                     heart_dome_centre(CAP_HEART_W, CAP_CENTER, CAP_TILT_DEG), CAP_DEPTH / 2.0)
    info = heart_shape(CAP_HEART_W)[1]
    shift = _rot((0.0, -(1 - CAP_INSET_SCALE) * (info['h'] - info['r']) / 2.0), CAP_TILT_DEG)
    inset_centre = (CAP_CENTER[0] + shift[0], CAP_CENTER[1] + shift[1])
    build_dome_heart(comp, 'Heart inset', cap_inset_outline(),
                     heart_dome_centre(CAP_HEART_W, inset_centre, CAP_TILT_DEG, CAP_INSET_SCALE),
                     CAP_DEPTH / 2.0 + CAP_INSET_PROUD)
    return comp


DOME_STEPS_DEG = (0.0, 30.0, 55.0, 72.0, 84.0)   # slices of the puffy heart


def build_dome_heart(comp, name, outline, peak, half_t):
    """Puffy heart: a loft through heart outlines stacked side to side, full
    size in the middle and shrinking smoothly (an elliptical profile) toward
    each side. Falls back to a thick heart with rounded edges if the loft
    can't be made."""
    def scaled(f):
        return [(seg[0],) + tuple((peak[0] + f * (q[0] - peak[0]), peak[1] + f * (q[1] - peak[1]))
                                  for q in seg[1:]) for seg in outline]
    try:
        profiles = []
        angles = [-a for a in reversed(DOME_STEPS_DEG[1:])] + list(DOME_STEPS_DEG)
        for a in angles:
            z = half_t * math.sin(math.radians(a))
            f = math.cos(math.radians(a))
            plane = None
            if abs(z) > 1e-6:
                plane = offset_plane(comp, comp.xYConstructionPlane, z, 'z', z)
            sk = side_sketch(comp, '{} slice {:+.0f}'.format(name, a), [scaled(f)], plane=plane)
            profiles.append(pick_profile(sk))
        lofts = comp.features.loftFeatures
        inp = lofts.createInput(NEW)
        for pr in profiles:
            inp.loftSections.add(pr)
        inp.isSolid = True
        body = lofts.add(inp).bodies.item(0)
        body.name = name
        return body
    except Exception:
        _skipped.append('{}: puffy loft failed, used a thick heart with rounded edges'.format(name))
    sk = side_sketch(comp, '{} outline'.format(name), [outline])
    body = extrude_sym(comp, pick_profile(sk), 2.0 * half_t, NEW, name=name).bodies.item(0)
    fillet(comp, body, 0.4 * 2.0 * half_t, name, edge_filter=flat_in('z'))
    return body_named(comp, name)


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

# Colour for any body whose name isn't in BODY_COLORS, by component
COMPONENT_COLORS = {
    'Slide': BODY_COLORS['Slide'],
    'Muzzle & Shroud': BODY_COLORS['Barrel'],
    'Frame & Grip': BODY_COLORS['Frame & Grip'],
    'Trigger': BODY_COLORS['Trigger'],
    'ADS Lever': BODY_COLORS['ADS lever'],
    'Switches (reference)': BODY_COLORS['Switch (reference)'],
    'Reload Button': BODY_COLORS['Reload button'],
    'Infuse Button': BODY_COLORS['Infuse button'],
    'Recenter Button': BODY_COLORS['Recenter button'],
    'LED Window': BODY_COLORS['LED window'],
    'Rear Cap (Heart)': BODY_COLORS['Heart cap'],
    'Charm': BODY_COLORS['Charm'],
}


def apply_colors(app, design):
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
        occs = design.rootComponent.allOccurrences
        for comp in [occs.item(i).component for i in range(occs.count)]:
            for b in bodies(comp):
                base_name = b.name[:-2] if b.name.endswith((' L', ' R')) else b.name   # split halves
                rgb = BODY_COLORS.get(base_name) or COMPONENT_COLORS.get(comp.name)
                if not rgb or not b.isSolid:
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
                               ('Trigger', build_trigger), ('ADS Lever', build_ads),
                               ('Switches (reference)', build_switch_refs), ('Reload Button', build_button),
                               ('Infuse Button', build_infuse), ('Recenter Button', build_recenter),
                               ('LED Window', build_led_window),
                               ('Rear Cap (Heart)', build_rear_cap), ('Charm', build_charm)):
            try:
                comps.append(builder(root))
            except Exception:
                _skipped.append('{} FAILED:\n{}'.format(label, traceback.format_exc(limit=2)))

        apply_colors(app, design)
        app.activeViewport.fit()

        msg = 'CYBER Celestia CGM ({}) built: {} parts.'.format(SCRIPT_VERSION, len(comps))
        if _skipped:
            msg += '\n\nNotes:\n- ' + '\n- '.join(_skipped)
        msg += '\n\nWidths and depths: Modify > Change Parameters.'
        ui.messageBox(msg, 'CYBER Celestia CGM')
    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
