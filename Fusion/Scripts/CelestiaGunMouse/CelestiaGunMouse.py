"""
CYBER Celestia - Custom Gun Mouse (CGM)
Starter model for Autodesk Fusion, built from concept sketch v1
(reference/concept-sketch-v1.webp).

HOW TO RUN
  Utilities > Add-Ins > Scripts and Add-Ins > "+" (Script or add-in from
  device) > pick this folder > select CelestiaGunMouse > Run.
  The script always opens a NEW design, so it never touches your other work.

WHAT YOU GET
  One component per labelled part of the sketch:
    Slide, Muzzle & Shroud (bore + front sight), Frame & Grip (trigger guard,
    readout window, charm eyelet), Trigger, Top Button, Rear Cap (heart +
    grip loop) and Charm.

EDITING
  * Thicknesses (side-to-side widths, cut depths) are live Fusion parameters:
    Modify > Change Parameters. Change them and the model updates.
  * Outlines (lengths, heights, angles, positions) are the numbers in the
    DIMENSIONS block below. Edit them and run the script again.

AXES (all numbers in millimetres)
  +X points toward the muzzle, +Y points up, Z is across the gun.
  -Z is the gun's LEFT side (the side shown in the sketch).
  y = 0 is where the slide sits on the frame.
"""

import math
import traceback

import adsk.core
import adsk.fusion


# =============================================================================
# DIMENSIONS (mm). Edit these, then re-run the script.
# =============================================================================

# Slide (the big top block)
SLIDE_LEN = 125.0          # rear face (x = 0) to front face
SLIDE_H = 30.0             # height above the frame
SLIDE_FRONT_CHAMFER = 5.0  # top-front bevel
SLIDE_REAR_CHAMFER = 5.0   # top-rear bevel
SERRATION_XS = (66.0, 73.0, 80.0)   # where the 3 slanted grooves start (bottom)
SERRATION_W = 2.5          # groove width
SERRATION_LEAN = 8.0       # how far forward the top of each groove leans

# Rear sight ("cat ears" just in front of the heart)
REAR_SIGHT_X = 5.0         # rear edge of the rear sight
REAR_SIGHT_LEN = 10.0
REAR_SIGHT_H = 8.0
REAR_SIGHT_NOTCH = 7.0     # gap between the two ears

# Muzzle / shroud (revolved around a horizontal axis)
BORE_AXIS_Y = 12.0         # height of the barrel centreline
SHROUD_LEN = 15.0          # collar between slide and muzzle
SHROUD_R = 15.0
MUZZLE_LEN = 18.0
MUZZLE_R = 18.0
MUZZLE_LIP_R = 14.0        # inner edge of the front lip ring
MUZZLE_RECESS = 2.0        # how far the face sits back inside the lip
BORE_R = 7.0
BORE_DEPTH = 15.0          # measured from the front of the muzzle

# Front sight (upright ring on top of the muzzle)
SIGHT_R_OUT = 6.0
SIGHT_R_IN = 3.5
SIGHT_X_FROM_FRONT = 8.0   # distance back from the muzzle face

# Frame (strip under the slide that holds the readout)
FRAME_REAR_X = 6.0
FRAME_FRONT_X = 122.0
FRAME_H = 16.0

# Readout window (recess on the frame's left side, for a small display)
READOUT_X0, READOUT_X1 = 72.0, 104.0
READOUT_Y0, READOUT_Y1 = -13.0, -3.0

# Grip
GRIP_TOP_REAR_X = 8.0      # back of the grip where it meets the frame
GRIP_TOP_FRONT_X = 52.0    # front of the grip where it meets the frame
GRIP_LEN = 90.0            # measured along the rake
GRIP_RAKE_DEG = 20.0       # lean of the grip back from vertical

# Trigger guard: the opening must fit your index finger (~20 mm).
GUARD_OUT_FRONT_X = 96.0
GUARD_OUT_BOTTOM_Y = -45.0
GUARD_IN_FRONT_X = 88.0
GUARD_IN_BOTTOM_Y = -38.0

# Heart rear cap (doubles as a beavertail/palm rest)
CAP_CENTER = (-12.0, 16.0)  # centre between the two lobes
CAP_HEART_W = 46.0          # lobe-to-lobe width before rotating
CAP_TILT_DEG = 45.0         # tilts the tip forward/down into the slide

# Grip loop (curved band from the heart down into the back of the grip).
# NOTE: as drawn, your palm sits inside this loop. Set False to leave it off.
INCLUDE_GRIP_LOOP = True
LOOP_START = (-24.0, -1.0)  # inside the heart's rear lobe
LOOP_MID = (-31.0, -26.0)   # furthest point behind the grip
LOOP_END = (-2.0, -50.0)    # inside the back of the grip
LOOP_BAND = 6.0             # band thickness seen from the side

# Charm eyelet on the frame + hanging heart charm
EYELET_CENTER = (110.0, -19.5)
EYELET_R_OUT, EYELET_R_IN = 4.0, 2.0
CHARM_CENTER = (112.0, -60.0)
CHARM_W = 16.0
CHARM_HOLE_R = 1.2

# Top button (the pill on top of the slide)
BUTTON_X0, BUTTON_X1 = 32.0, 48.0
BUTTON_H = 4.0

# Fillet radii (if a fillet fails, the script skips it and tells you)
FILLET_SLIDE = 2.0
FILLET_FRAME = 2.0
FILLET_GRIP = 6.0
FILLET_GUARD = 2.0
FILLET_CAP = 5.0
FILLET_SMALL = 1.0

# Live parameters: (name, value in mm, comment). Shown in Change Parameters.
LIVE_PARAMS = [
    ('slide_width', 28.0, 'Slide thickness, side to side'),
    ('frame_width', 24.0, 'Frame thickness, side to side'),
    ('grip_width', 30.0, 'Grip thickness, side to side'),
    ('guard_width', 12.0, 'Trigger guard thickness'),
    ('trigger_width', 7.0, 'Trigger blade thickness'),
    ('button_width', 10.0, 'Top button width'),
    ('cap_width', 26.0, 'Heart rear cap thickness'),
    ('loop_width', 10.0, 'Grip loop thickness'),
    ('sight_thickness', 3.0, 'Front sight ring thickness'),
    ('charm_thickness', 4.0, 'Heart charm thickness'),
    ('eyelet_thickness', 4.0, 'Charm eyelet thickness'),
    ('serration_depth', 1.0, 'Depth of the slide grooves'),
    ('readout_depth', 1.5, 'Depth of the readout window recess'),
]

# Colours from the sketch (R, G, B)
COLORS = {
    'Slide': (232, 72, 170),
    'Muzzle & Shroud': (248, 176, 222),
    'Frame & Grip': (246, 140, 205),
    'Trigger': (200, 70, 160),
    'Top Button': (225, 60, 150),
    'Rear Cap (Heart)': (252, 242, 185),
    'Charm': (215, 55, 145),
}


# =============================================================================
# 2D OUTLINES (pure geometry, no Fusion calls).
# A loop is a list of segments:
#   ('line', p0, p1)        straight line
#   ('arc', p0, pmid, p1)   arc through three points
#   ('circle', c, r)        full circle
# Points are (x, y) in the side view unless noted.
# =============================================================================

def _rot(p, deg, about=(0.0, 0.0)):
    a = math.radians(deg)
    x, y = p[0] - about[0], p[1] - about[1]
    return (about[0] + x * math.cos(a) - y * math.sin(a),
            about[1] + x * math.sin(a) + y * math.cos(a))


def polygon(pts):
    return [('line', pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def transform(loop, deg=0.0, offset=(0.0, 0.0)):
    out = []
    for seg in loop:
        if seg[0] == 'circle':
            c = _rot(seg[1], deg)
            out.append(('circle', (c[0] + offset[0], c[1] + offset[1]), seg[2]))
        else:
            pts = [_rot(p, deg) for p in seg[1:]]
            out.append((seg[0],) + tuple((p[0] + offset[0], p[1] + offset[1]) for p in pts))
    return out


def heart(width, center=(0.0, 0.0), tilt_deg=0.0):
    """Heart from two circular lobes and two straight sides to a point.
    `center` is midway between the lobe centres; the tip points down
    before tilting (positive tilt = counter-clockwise)."""
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

    def arc_mid(cx, p0, p1, ccw):
        a0 = math.atan2(p0[1], p0[0] - cx)
        a1 = math.atan2(p1[1], p1[0] - cx)
        if ccw and a1 < a0:
            a1 += 2 * math.pi
        if not ccw and a1 > a0:
            a1 -= 2 * math.pi
        m = (a0 + a1) / 2
        return (cx + r * math.cos(m), r * math.sin(m))

    tr = tangent_point(a, +1)
    tl = tangent_point(-a, -1)
    loop = [
        ('line', tip, tr),
        ('arc', tr, arc_mid(a, tr, cusp, True), cusp),
        ('arc', cusp, arc_mid(-a, cusp, tl, True), tl),
        ('line', tl, tip),
    ]
    return transform(loop, tilt_deg, center)


def circle_through(p0, p1, p2):
    ax, ay = p0
    bx, by = p1
    cx, cy = p2
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


def arc_band(p0, pm, p1, thickness):
    """Closed band of constant thickness centred on the arc p0 -> pm -> p1."""
    c, r = circle_through(p0, pm, p1)
    t = thickness / 2.0

    def on(p, rr):
        ang = math.atan2(p[1] - c[1], p[0] - c[0])
        return (c[0] + rr * math.cos(ang), c[1] + rr * math.sin(ang))

    o0, om, o1 = on(p0, r + t), on(pm, r + t), on(p1, r + t)
    i0, im, i1 = on(p0, r - t), on(pm, r - t), on(p1, r - t)
    return [('arc', o0, om, o1), ('line', o1, i1), ('arc', i1, im, i0), ('line', i0, o0)]


def slide_outline():
    L, H = SLIDE_LEN, SLIDE_H
    return polygon([(0, 0), (L, 0), (L, H - SLIDE_FRONT_CHAMFER),
                    (L - SLIDE_FRONT_CHAMFER, H), (SLIDE_REAR_CHAMFER, H),
                    (0, H - SLIDE_REAR_CHAMFER)])


def rear_sight_outline():
    x0, y0 = REAR_SIGHT_X, SLIDE_H - 1.0   # sinks 1 mm into the slide
    return polygon([(x0, y0), (x0 + REAR_SIGHT_LEN, y0),
                    (x0 + REAR_SIGHT_LEN * 0.3, SLIDE_H + REAR_SIGHT_H),
                    (x0, SLIDE_H + REAR_SIGHT_H * 0.75)])


def serration_outlines():
    y0, y1 = 4.0, SLIDE_H - 4.0
    return [polygon([(x, y0), (x + SERRATION_W, y0),
                     (x + SERRATION_W + SERRATION_LEAN, y1), (x + SERRATION_LEAN, y1)])
            for x in SERRATION_XS]


def muzzle_x_positions():
    x0 = SLIDE_LEN
    x1 = x0 + SHROUD_LEN
    x2 = x1 + MUZZLE_LEN
    return x0, x1, x2


def muzzle_half_section():
    """Half cross-section revolved around y = BORE_AXIS_Y. The first segment
    is the axis itself."""
    x0, x1, x2 = muzzle_x_positions()
    y = BORE_AXIS_Y
    bore_bottom = x2 - BORE_DEPTH
    face = x2 - MUZZLE_RECESS
    pts = [(bore_bottom, y), (x0, y), (x0, y + SHROUD_R), (x1, y + SHROUD_R),
           (x1, y + MUZZLE_R), (x2, y + MUZZLE_R), (x2, y + MUZZLE_LIP_R),
           (face, y + MUZZLE_LIP_R), (face, y + BORE_R), (bore_bottom, y + BORE_R)]
    return polygon(pts)


def front_sight_loops():
    _, _, x2 = muzzle_x_positions()
    c = (x2 - SIGHT_X_FROM_FRONT, BORE_AXIS_Y + MUZZLE_R + SIGHT_R_OUT - 1.0)
    return [[('circle', c, SIGHT_R_OUT)], [('circle', c, SIGHT_R_IN)]]


def frame_outline():
    r, f, h = FRAME_REAR_X, FRAME_FRONT_X, FRAME_H
    return [
        ('line', (r, 0), (f, 0)),
        ('line', (f, 0), (f, -6)),
        ('arc', (f, -6), (f - 6, -h + 3), (f - 16, -h)),
        ('line', (f - 16, -h), (r + 4, -h)),
        ('line', (r + 4, -h), (r, -h + 4)),
        ('line', (r, -h + 4), (r, 0)),
    ]


def grip_line_x(x_top, y):
    """x of a grip edge (front or back) at height y, given where it meets the frame."""
    return x_top + (y + FRAME_H) * math.tan(math.radians(GRIP_RAKE_DEG))


def grip_outline():
    top = -FRAME_H + 6.0                                   # overlaps the frame
    bottom = -FRAME_H - GRIP_LEN * math.cos(math.radians(GRIP_RAKE_DEG))
    return polygon([(grip_line_x(GRIP_TOP_REAR_X, top), top),
                    (grip_line_x(GRIP_TOP_FRONT_X, top), top),
                    (grip_line_x(GRIP_TOP_FRONT_X, bottom), bottom),
                    (grip_line_x(GRIP_TOP_REAR_X, bottom), bottom)])


def guard_loops():
    h = FRAME_H
    fx, by = GUARD_OUT_FRONT_X, GUARD_OUT_BOTTOM_Y
    ifx, iby = GUARD_IN_FRONT_X, GUARD_IN_BOTTOM_Y
    gfx = GRIP_TOP_FRONT_X
    outer = [
        ('line', (gfx - 12, -h + 2), (fx, -h + 2)),
        ('arc', (fx, -h + 2), (fx + 5, (-h + by) / 2), (fx - 10, by)),
        ('line', (fx - 10, by), (grip_line_x(gfx, by) - 3, by)),
        ('line', (grip_line_x(gfx, by) - 3, by), (gfx - 12, -h + 2)),
    ]
    rear_top = (gfx + 2, -h)
    rear_bot = (grip_line_x(gfx, iby) + 6, iby)
    inner = [
        ('line', rear_top, (ifx, -h)),
        ('arc', (ifx, -h), (ifx + 4, (-h + iby) / 2 - 0.5), (ifx - 6, iby)),
        ('line', (ifx - 6, iby), rear_bot),
        ('line', rear_bot, rear_top),
    ]
    return [outer, inner]


def trigger_outline():
    h = FRAME_H
    return [
        ('line', (68, -h), (76, -h)),
        ('arc', (76, -h), (75, -h - 10), (67, -h - 17)),
        ('line', (67, -h - 17), (64, -h - 15)),
        ('arc', (64, -h - 15), (68.5, -h - 8), (68, -h)),
    ]


def readout_outline():
    return polygon([(READOUT_X0, READOUT_Y0), (READOUT_X1, READOUT_Y0),
                    (READOUT_X1, READOUT_Y1), (READOUT_X0, READOUT_Y1)])


def eyelet_loops():
    c = EYELET_CENTER
    ring = [[('circle', c, EYELET_R_OUT)], [('circle', c, EYELET_R_IN)]]
    tab = polygon([(c[0] - 2.5, c[1] + EYELET_R_IN + 0.8), (c[0] + 2.5, c[1] + EYELET_R_IN + 0.8),
                   (c[0] + 2.5, -FRAME_H + 4), (c[0] - 2.5, -FRAME_H + 4)])
    return ring, tab


def button_outline():
    x0, x1, y0, y1 = BUTTON_X0, BUTTON_X1, SLIDE_H, SLIDE_H + BUTTON_H
    rr = BUTTON_H / 2.0
    ym = (y0 + y1) / 2.0
    return [
        ('line', (x0 + rr, y0), (x1 - rr, y0)),
        ('arc', (x1 - rr, y0), (x1, ym), (x1 - rr, y1)),
        ('line', (x1 - rr, y1), (x0 + rr, y1)),
        ('arc', (x0 + rr, y1), (x0, ym), (x0 + rr, y0)),
    ]


def cap_outline():
    return heart(CAP_HEART_W, CAP_CENTER, CAP_TILT_DEG)


def grip_loop_outline():
    return arc_band(LOOP_START, LOOP_MID, LOOP_END, LOOP_BAND)


def charm_loops():
    cx, cy = CHARM_CENTER
    r = CHARM_W / 3.2
    hole = (cx, cy + 0.8 * r - 1.2 - CHARM_HOLE_R - 1.0)
    return [heart(CHARM_W, CHARM_CENTER), [('circle', hole, CHARM_HOLE_R)]]


# =============================================================================
# FUSION HELPERS
# =============================================================================

_skipped = []   # things that could not be built (shown at the end)


def cm(v_mm):
    return v_mm / 10.0


def vi(v):
    """ValueInput from a number (mm) or a parameter expression string."""
    if isinstance(v, str):
        return adsk.core.ValueInput.createByString(v)
    return adsk.core.ValueInput.createByReal(cm(v))


def sk_point(sketch, x, y, z):
    p = sketch.modelToSketchSpace(adsk.core.Point3D.create(cm(x), cm(y), cm(z)))
    return adsk.core.Point3D.create(p.x, p.y, 0)


def draw_loops(sketch, loops, to3d):
    """Draw loops into a sketch. to3d maps a 2D outline point to model (x, y, z) mm."""
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
    _merge_endpoints(sketch)


def _merge_endpoints(sketch, tol=1e-5):
    """Join coincident line/arc ends so loops are properly connected."""
    seen = []
    for i in range(sketch.sketchPoints.count):
        sp = sketch.sketchPoints.item(i)
        seen.append(sp)
    keep = []
    for sp in seen:
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


def side_sketch(comp, name, loops, plane=None, z=0.0):
    """Sketch side-view loops (x, y) on the XY plane or a plane parallel to it."""
    sk = comp.sketches.add(plane or comp.xYConstructionPlane)
    sk.name = name
    draw_loops(sk, loops, lambda p: (p[0], p[1], z))
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


def smallest_profile(sketch):
    best, best_area = None, None
    for i in range(sketch.profiles.count):
        pr = sketch.profiles.item(i)
        area = pr.areaProperties(adsk.fusion.CalculationAccuracy.LowCalculationAccuracy).area
        if best_area is None or area < best_area:
            best, best_area = pr, area
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


def on_side_face(edge):
    """True for edges lying flat on a +Z/-Z face. Use for outlines with
    tangent (smooth) joins, whose across-the-gun edges can't be filleted."""
    bb = edge.boundingBox
    return abs(bb.maxPoint.z - bb.minPoint.z) < 1e-4


def new_component(root, name):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def first_body(comp):
    return comp.bRepBodies.item(0)


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
    slide = first_body(comp)

    # Rear sight: a block with a notch cut down the middle -> two "ears"
    sk = side_sketch(comp, 'Rear sight profile', [rear_sight_outline()])
    sight = extrude_sym(comp, pick_profile(sk), 'slide_width - 8 mm', NEW, name='Rear sight').bodies.item(0)
    notch_x = REAR_SIGHT_X + REAR_SIGHT_LEN / 2.0
    pl = offset_plane(comp, comp.yZConstructionPlane, notch_x, 'x', notch_x)
    nsk = comp.sketches.add(pl)
    nsk.name = 'Rear sight notch'
    half = REAR_SIGHT_NOTCH / 2.0
    y0, y1 = SLIDE_H + 0.5, SLIDE_H + REAR_SIGHT_H + 5
    draw_loops(nsk, [polygon([(-half, y0), (half, y0), (half, y1), (-half, y1)])],
               lambda p: (notch_x, p[1], p[0]))
    extrude_sym(comp, pick_profile(nsk), REAR_SIGHT_LEN * 3, CUT, participants=[sight])
    combine_join(comp, slide, [b for b in _bodies(comp) if b.name != 'Slide'])
    slide = first_body(comp)

    # Slanted grooves on both sides
    for side, label in ((1, 'right'), (-1, 'left')):
        expr = 'slide_width / 2' if side > 0 else '-slide_width / 2'
        pl = offset_plane(comp, comp.xYConstructionPlane, expr, 'z', side * 14.0)
        sk = comp.sketches.add(pl)
        sk.name = 'Serrations ({})'.format(label)
        draw_loops(sk, serration_outlines(), lambda p: (p[0], p[1], 0.0))
        try:
            extrude_sym(comp, all_profiles(sk), 'serration_depth * 2', CUT, participants=[slide])
        except Exception:
            _skipped.append('Slide: {} serrations skipped'.format(label))
    return comp


def _bodies(comp):
    return [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]


def build_muzzle(root):
    comp = new_component(root, 'Muzzle & Shroud')
    sk = side_sketch(comp, 'Muzzle half-section', [muzzle_half_section()])
    axis = sk.sketchCurves.sketchLines.item(0)   # first segment = the bore axis
    revs = comp.features.revolveFeatures
    inp = revs.createInput(pick_profile(sk), axis, NEW)
    inp.setAngleExtent(False, adsk.core.ValueInput.createByString('360 deg'))
    muzzle = revs.add(inp).bodies.item(0)
    muzzle.name = 'Muzzle'

    sk = side_sketch(comp, 'Front sight ring', front_sight_loops())
    extrude_sym(comp, pick_profile(sk, loops=2), 'sight_thickness', JOIN, participants=[muzzle])
    fillet(comp, first_body(comp), FILLET_SMALL, 'Front sight',
           edge_filter=lambda e: e.boundingBox.maxPoint.y * 10 > BORE_AXIS_Y + MUZZLE_R + 0.5)
    return comp


def build_frame(root):
    comp = new_component(root, 'Frame & Grip')

    sk = side_sketch(comp, 'Frame profile', [frame_outline()])
    frame = extrude_sym(comp, pick_profile(sk), 'frame_width', NEW, name='Frame').bodies.item(0)
    fillet(comp, frame, FILLET_FRAME, 'Frame')
    frame = first_body(comp)

    sk = side_sketch(comp, 'Grip profile', [grip_outline()])
    grip = extrude_sym(comp, pick_profile(sk), 'grip_width', NEW, name='Grip').bodies.item(0)
    top_cut = (-FRAME_H + 5.0) / 10.0     # leave the edges hidden inside the frame sharp
    fillet(comp, grip, FILLET_GRIP, 'Grip', edge_filter=lambda e: e.boundingBox.minPoint.y < top_cut)

    sk = side_sketch(comp, 'Trigger guard profile', guard_loops())
    guard = extrude_sym(comp, pick_profile(sk, loops=2), 'guard_width', NEW, name='Guard').bodies.item(0)
    fillet(comp, guard, FILLET_GUARD, 'Trigger guard')

    ring_loops, tab = eyelet_loops()
    sk = side_sketch(comp, 'Charm eyelet', ring_loops)
    extrude_sym(comp, pick_profile(sk, loops=2), 'eyelet_thickness', NEW, name='Eyelet')
    sk = side_sketch(comp, 'Charm eyelet tab', [tab])
    extrude_sym(comp, pick_profile(sk), 'eyelet_thickness', NEW, name='Eyelet tab')

    frame = [b for b in _bodies(comp) if b.name == 'Frame'][0]
    combine_join(comp, frame, [b for b in _bodies(comp) if b.name != 'Frame'])
    frame = first_body(comp)
    frame.name = 'Frame & Grip'

    # Readout window recess on the left side (-Z)
    pl = offset_plane(comp, comp.xYConstructionPlane, '-frame_width / 2', 'z', -12.0)
    sk = comp.sketches.add(pl)
    sk.name = 'Readout window'
    draw_loops(sk, [readout_outline()], lambda p: (p[0], p[1], 0.0))
    extrude_sym(comp, pick_profile(sk), 'readout_depth * 2', CUT, participants=[frame])
    return comp


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
    base = SLIDE_H / 10.0 + 0.05
    fillet(comp, body, FILLET_SMALL, 'Top button',
           edge_filter=lambda e: on_side_face(e) and e.boundingBox.maxPoint.y > base)
    return comp


def build_rear_cap(root):
    comp = new_component(root, 'Rear Cap (Heart)')
    sk = side_sketch(comp, 'Heart profile', [cap_outline()])
    cap = extrude_sym(comp, pick_profile(sk), 'cap_width', NEW, name='Heart cap').bodies.item(0)
    fillet(comp, cap, FILLET_CAP, 'Heart cap', edge_filter=on_side_face)
    if INCLUDE_GRIP_LOOP:
        cap = first_body(comp)
        sk = side_sketch(comp, 'Grip loop profile', [grip_loop_outline()])
        loop = extrude_sym(comp, pick_profile(sk), 'loop_width', NEW, name='Grip loop').bodies.item(0)
        fillet(comp, loop, 2.5, 'Grip loop')
        combine_join(comp, cap, [b for b in _bodies(comp) if b.name != 'Heart cap'])
    return comp


def build_charm(root):
    comp = new_component(root, 'Charm')
    sk = side_sketch(comp, 'Charm profile', charm_loops())
    body = extrude_sym(comp, pick_profile(sk, loops=2), 'charm_thickness', NEW, name='Charm').bodies.item(0)
    fillet(comp, body, FILLET_SMALL, 'Charm', edge_filter=on_side_face)
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
        for comp in comps:
            rgb = COLORS.get(comp.name)
            if not rgb:
                continue
            ap = design.appearances.addByCopy(base, 'Celestia ' + comp.name)
            for k in range(ap.appearanceProperties.count):
                prop = adsk.core.ColorProperty.cast(ap.appearanceProperties.item(k))
                if prop:
                    prop.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
                    break
            for b in _bodies(comp):
                b.appearance = ap
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
        root.name = 'CYBER Celestia CGM'

        for name, value, comment in LIVE_PARAMS:
            design.userParameters.add(name, adsk.core.ValueInput.createByString('{} mm'.format(value)),
                                      'mm', comment)

        comps = []
        for label, builder in (('Slide', build_slide), ('Muzzle & Shroud', build_muzzle),
                               ('Frame & Grip', build_frame), ('Trigger', build_trigger),
                               ('Top Button', build_button), ('Rear Cap (Heart)', build_rear_cap),
                               ('Charm', build_charm)):
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
