"""Generate the animated gym illustrations, tai chi and posture. Run: python3 make-illustrations.py

Simple original pictogram figures — not photos, not anyone's likeness — matching the app's own
dark/gold visual style (same palette as ../make-icon.py). Arms are a single straight capsule
from shoulder to hand (no elbow): two segments converging near the body's centre line — e.g.
hands clasped at the chest — draws an unavoidable "kite" shape with an elbow joint, so the
hand position alone has to carry each pose. Legs keep a knee joint since long straight legs
read fine and a squat needs the bend. Each pose is a small set of joint coordinates on a
normalised 0-1 grid (x: left->right, y: top->bottom).

Each movement is a short list of key poses. The figure eases from one to the next, pauses
briefly on each, and loops, saved as an animated WebP (photos/tai-chi/, photos/posture/).
Most loop there and back (A-B-A); `loop=True` runs the keys in a circle instead (A-B-C-D-A),
which is how alternating-side moves show both sides.

Rerun this if you want to change a pose; the JSON image paths don't need to change.
"""

import math
import os

from PIL import Image, ImageDraw

BG_TOP = (26, 31, 43)
BG_BOTTOM = (13, 15, 20)
GOLD = (217, 169, 76)

W, H = 640, 760  # squarish on purpose: a tall narrow canvas made the figure read as a thin skewer
SCALE = 3  # supersample then downscale for smooth anti-aliased lines


FPS = 15


def _make_bg(s_w, s_h):
    img = Image.new("RGB", (s_w, s_h))
    d = ImageDraw.Draw(img)
    for y in range(s_h):
        t = y / (s_h - 1)
        d.line([(0, y), (s_w, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)))
    return img


_BG = None


def bg(s_w, s_h):
    # the gradient is the slow part of a frame, so draw it once and copy it
    global _BG
    if _BG is None:
        _BG = _make_bg(s_w, s_h)
    img = _BG.copy()
    return img, ImageDraw.Draw(img)


def capsule(d, p1, p2, w, r):
    d.line([p1, p2], fill=GOLD, width=w)
    for p in (p1, p2):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=GOLD)


PROP = (110, 110, 110)


def draw_pose(pose, ground=True, props=(), band=False):
    s_w, s_h = W * SCALE, H * SCALE
    img, d = bg(s_w, s_h)

    def pt(key):
        x, y = pose[key]
        return (x * s_w, y * s_h)

    lw = max(2, int(s_h * 0.026))
    jr = lw * 0.62

    if ground:
        gy = 0.97 * s_h
        d.line([(0.08 * s_w, gy), (0.92 * s_w, gy)], fill=(60, 67, 82), width=max(1, int(s_h * 0.004)))

    # props (wall, bench) sit behind the figure: (x1, y1, x2, y2) rectangles, drawn as outlines
    for x1, y1, x2, y2 in props:
        d.rectangle([x1 * s_w, y1 * s_h, x2 * s_w, y2 * s_h], outline=PROP, width=max(1, int(s_h * 0.006)))

    # torso (shoulder-centre to pelvis)
    capsule(d, pt('neck'), pt('pelvis'), lw, jr)
    # arms: single straight capsule, shoulder -> hand (no elbow — see module docstring)
    capsule(d, pt('l_shoulder'), pt('l_hand'), lw, jr)
    capsule(d, pt('r_shoulder'), pt('r_hand'), lw, jr)
    # legs: hip -> knee -> foot
    capsule(d, pt('pelvis'), pt('l_knee'), lw, jr)
    capsule(d, pt('l_knee'), pt('l_foot'), lw, jr)
    capsule(d, pt('pelvis'), pt('r_knee'), lw, jr)
    capsule(d, pt('r_knee'), pt('r_foot'), lw, jr)
    # a resistance band or towel held taut between the hands
    if band:
        d.line([pt('l_hand'), pt('r_hand')], fill=GOLD, width=max(1, int(lw * 0.35)))
    # head, drawn last so it sits cleanly on top of the shoulder line
    hx, hy = pt('head')
    r = 0.072 * s_h
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=GOLD)
    d.ellipse([hx - r * 0.62, hy - r * 0.62, hx + r * 0.62, hy + r * 0.62],
              fill=tuple(round(a + (b - a) * (hy / s_h)) for a, b in zip(BG_TOP, BG_BOTTOM)))

    return img.resize((W, H), Image.LANCZOS)


# Baseline standing joints, overridden per pose below. Shoulders sit below and outside the
# head so overhead arms swing past it rather than through it.
BASE = dict(
    head=(0.5, 0.11), neck=(0.5, 0.215), pelvis=(0.5, 0.57),
    l_shoulder=(0.40, 0.225), l_hand=(0.36, 0.47),
    r_shoulder=(0.60, 0.225), r_hand=(0.64, 0.47),
    l_knee=(0.43, 0.78), l_foot=(0.41, 0.96),
    r_knee=(0.57, 0.78), r_foot=(0.59, 0.96),
)
UPPER = ('head', 'neck', 'l_shoulder', 'r_shoulder', 'l_hand', 'r_hand')


def pose(**overrides):
    p = dict(BASE)
    p.update(overrides)
    return p


def mirror(p):
    """The same pose on the other side: swap left/right and flip x."""
    out = {}
    for k, (x, y) in p.items():
        k2 = 'r_' + k[2:] if k.startswith('l_') else 'l_' + k[2:] if k.startswith('r_') else k
        out[k2] = (1 - x, y)
    return out


def shift(p, dy, keys=None):
    return {k: (x, y + dy) if keys is None or k in keys else (x, y) for k, (x, y) in p.items()}


STAND = pose()


# ---- Tai chi ---------------------------------------------------------------------------

# small hop, feet lifted off the ground, arms relaxed at the hips
HOP_LAND = shift(pose(l_hand=(0.38, 0.52), r_hand=(0.62, 0.52), pelvis=(0.5, 0.59),
                      l_knee=(0.45, 0.79), r_knee=(0.55, 0.79)), 0.02, UPPER)
HOP_AIR = shift(pose(l_hand=(0.38, 0.50), r_hand=(0.62, 0.50)), -0.06)
# both arms reach straight overhead, torso curved into the wave
WAVE_UP = pose(pelvis=(0.53, 0.57), l_hand=(0.34, -0.02), r_hand=(0.68, -0.02))
WAVE_DOWN = shift(pose(pelvis=(0.47, 0.62), l_hand=(0.40, 0.33), r_hand=(0.60, 0.33),
                       l_knee=(0.42, 0.80), r_knee=(0.56, 0.80)), 0.03, UPPER)
# one arm swung up and back, the other forward and down
ARM_SWING = pose(l_hand=(0.26, 0.58), r_hand=(0.78, 0.02))
# feet wide, shoulders rotated, both hands swung round to one side at chest height
# (crossed hands mirror onto themselves, so the swing has to carry the twist)
TRUNK_TWIST = pose(
    l_foot=(0.30, 0.96), r_foot=(0.70, 0.96),
    l_shoulder=(0.44, 0.22), r_shoulder=(0.58, 0.25),
    l_hand=(0.74, 0.36), r_hand=(0.84, 0.42),
)
# arms sweep down -> out -> overhead and back, mid-circle shown as arms out to the sides
CIRCLE_DOWN = pose(l_hand=(0.33, 0.48), r_hand=(0.67, 0.48))
CIRCLE_OUT = pose(l_hand=(0.12, 0.28), r_hand=(0.88, 0.28))
CIRCLE_UP = pose(l_hand=(0.36, -0.02), r_hand=(0.64, -0.02))
# deep knee bend, arms hanging straight for balance, feet wide
SQUAT = shift(pose(
    pelvis=(0.5, 0.68),
    l_hand=(0.40, 0.50), r_hand=(0.60, 0.50),
    l_knee=(0.38, 0.80), l_foot=(0.34, 0.96), r_knee=(0.62, 0.80), r_foot=(0.66, 0.96),
), 0.10, UPPER)
SQUAT_TOP = pose(l_foot=(0.34, 0.96), r_foot=(0.66, 0.96), l_knee=(0.39, 0.77), r_knee=(0.61, 0.77))
# arms crossed over the chest, then flung loosely open
DEAD_ARMS_IN = pose(l_hand=(0.58, 0.26), r_hand=(0.42, 0.28))
DEAD_ARMS_OUT = pose(l_hand=(0.16, 0.42), r_hand=(0.84, 0.42))
# one arm raised high on the diagonal, the other swept low across the body
GOLF = pose(pelvis=(0.46, 0.57), l_hand=(0.30, 0.56), r_hand=(0.80, -0.03))
# right knee driven up high, opposite arm forward — mid-march. Hands stay on their own
# side (never crossing the centre line) so the raised knee doesn't get lost in an X of limbs.
MARCH = pose(
    l_hand=(0.30, 0.28), r_hand=(0.70, 0.55),
    l_knee=(0.44, 0.77), l_foot=(0.42, 0.96),
    r_knee=(0.60, 0.42), r_foot=(0.58, 0.50),
)
# arms swung low and back, then up on the toes with both arms overhead
TIPTOE_DOWN = pose(l_hand=(0.30, 0.52), r_hand=(0.70, 0.52))
TIPTOE_UP = pose(l_hand=(0.34, -0.03), r_hand=(0.66, -0.03),
                 l_knee=(0.46, 0.75), l_foot=(0.46, 0.93), r_knee=(0.54, 0.75), r_foot=(0.54, 0.93))
# one arm extended straight out to the side, torso twisted
TWIST_WAIST = pose(
    l_foot=(0.38, 0.96), r_foot=(0.62, 0.96),
    l_hand=(0.36, 0.52), r_hand=(0.90, 0.34),
)
# arms wide (T shape), one leg stepped back into a small lunge
WIDE_ARMS = pose(l_hand=(0.06, 0.28), r_hand=(0.94, 0.28))
WIDE_STEP = pose(
    l_hand=(0.06, 0.28), r_hand=(0.94, 0.28),
    l_knee=(0.45, 0.75), l_foot=(0.46, 0.88), r_knee=(0.62, 0.85), r_foot=(0.72, 0.98),
)
# lunge stance, both arms reaching up and over to one side
WAVE_LUNGE = pose(
    l_hand=(0.24, 0.00), r_hand=(0.56, -0.08),
    l_knee=(0.42, 0.74), l_foot=(0.42, 0.88), r_knee=(0.68, 0.86), r_foot=(0.80, 0.98),
)
# wide plie stance, arms raised overhead and well apart
BALLET_DOWN = shift(pose(
    pelvis=(0.5, 0.66),
    l_hand=(0.32, -0.04), r_hand=(0.68, -0.04),
    l_knee=(0.32, 0.79), l_foot=(0.24, 0.96), r_knee=(0.68, 0.79), r_foot=(0.76, 0.96),
), 0.08, UPPER)
BALLET_UP = pose(
    l_hand=(0.32, -0.04), r_hand=(0.68, -0.04),
    l_knee=(0.34, 0.77), l_foot=(0.24, 0.96), r_knee=(0.66, 0.77), r_foot=(0.76, 0.96),
)

TAI_CHI = {
    '01-lymphatic-hops': dict(keys=[HOP_LAND, HOP_AIR], move=0.25, hold=0.05),
    '02-body-waves': dict(keys=[WAVE_UP, WAVE_DOWN], move=1.0),
    '03-arm-swings': dict(keys=[ARM_SWING, mirror(ARM_SWING)], move=0.7),
    '04-trunk-twists': dict(keys=[TRUNK_TWIST, mirror(TRUNK_TWIST)], move=0.7),
    '05-forward-arm-circles': dict(keys=[CIRCLE_DOWN, CIRCLE_OUT, CIRCLE_UP], move=0.45, hold=0.0),
    '06-squats': dict(keys=[SQUAT_TOP, SQUAT], move=1.0),
    '07-backward-arm-swings': dict(keys=[mirror(ARM_SWING), ARM_SWING], move=0.7),
    '08-dead-arms': dict(keys=[DEAD_ARMS_IN, DEAD_ARMS_OUT], move=0.5, hold=0.05),
    '09-golf-swings': dict(keys=[GOLF, mirror(GOLF)], move=0.8),
    '10-marches': dict(keys=[MARCH, mirror(MARCH)], move=0.5),
    '11-tiptoe-arm-swings': dict(keys=[TIPTOE_DOWN, TIPTOE_UP], move=0.8),
    '12-twist-the-waist': dict(keys=[TWIST_WAIST, mirror(TWIST_WAIST)], move=0.7),
    '13-wide-arm-step-backs': dict(keys=[WIDE_ARMS, WIDE_STEP, WIDE_ARMS, mirror(WIDE_STEP)], move=0.7, loop=True),
    '14-back-step-wave-lunges': dict(keys=[STAND, WAVE_LUNGE, STAND, mirror(WAVE_LUNGE)], move=0.8, loop=True),
    '15-ballet-squats': dict(keys=[BALLET_UP, BALLET_DOWN], move=1.0),
}


# ---- Posture ---------------------------------------------------------------------------
# Floor exercises are drawn side-on (figure faces left, ground at y=0.97), with both
# shoulders and both hands near the same point since one arm hides the other. A figure lying
# full length is wider than the canvas, so floor poses run slightly short in the leg.

def floor(head, neck, pelvis, hands, knees, feet):
    """Side-on pose: both shoulders sit at the neck, the far limbs just behind the near ones."""
    (lh, rh), (lk, rk), (lf, rf) = hands, knees, feet
    return dict(head=head, neck=neck, pelvis=pelvis,
                l_shoulder=neck, r_shoulder=(neck[0] + 0.01, neck[1]),
                l_hand=lh, r_hand=rh, l_knee=lk, r_knee=rk, l_foot=lf, r_foot=rf)


PRONE_LEGS = dict(knees=((0.75, 0.94), (0.75, 0.94)), feet=((0.94, 0.95), (0.94, 0.95)))

POSTURE = {
    # band in front of the thighs, swept overhead with straight arms, and back
    'over-and-backs': dict(keys=[
        pose(l_hand=(0.20, 0.52), r_hand=(0.80, 0.52)),
        pose(l_hand=(0.22, 0.04), r_hand=(0.78, 0.04)),
    ], move=1.2, hold=0.3, band=True),
    # face down, then chest lifted by the back with the arms only steadying
    'cobra': dict(keys=[
        floor((0.12, 0.90), (0.25, 0.915), (0.55, 0.925), ((0.27, 0.955), (0.29, 0.955)), **PRONE_LEGS),
        floor((0.175, 0.65), (0.27, 0.72), (0.55, 0.92), ((0.27, 0.955), (0.29, 0.955)), **PRONE_LEGS),
    ], move=1.3, hold=0.8),
    # arm relaxed, then reaching up and out on the diagonal, held
    'stand-and-reach': dict(keys=[STAND, pose(r_hand=(0.80, 0.03))], move=1.0, hold=0.8),
    # on all fours: the hand threads under the body, then rotates straight up to the ceiling
    'quadruped-rotations': dict(keys=[
        floor((0.18, 0.64), (0.30, 0.68), (0.66, 0.74), ((0.30, 0.955), (0.52, 0.90)),
              ((0.64, 0.955), (0.66, 0.955)), ((0.86, 0.955), (0.88, 0.955))),
        floor((0.18, 0.64), (0.30, 0.68), (0.66, 0.74), ((0.30, 0.955), (0.33, 0.42)),
              ((0.64, 0.955), (0.66, 0.955)), ((0.86, 0.955), (0.88, 0.955))),
    ], move=1.0, hold=0.4),
    # standing against a wall (the panel behind): arms low and wide, slid up into a Y
    'wall-slides': dict(keys=[
        pose(l_hand=(0.16, 0.26), r_hand=(0.84, 0.26)),
        pose(l_hand=(0.30, 0.04), r_hand=(0.70, 0.04)),
    ], move=1.0, hold=0.2, props=[(0.14, 0.02, 0.86, 0.97)]),
    # face down: arms lifted forward into the Y, circled back to rest on the lower back
    'prone-arm-circles': dict(keys=[
        floor((0.14, 0.905), (0.28, 0.90), (0.64, 0.92), ((0.14, 0.64), (0.17, 0.66)),
              ((0.80, 0.935), (0.80, 0.935)), ((0.95, 0.945), (0.95, 0.945))),
        floor((0.14, 0.905), (0.28, 0.90), (0.64, 0.92), ((0.50, 0.85), (0.52, 0.86)),
              ((0.80, 0.935), (0.80, 0.935)), ((0.95, 0.945), (0.95, 0.945))),
    ], move=1.4, hold=0.3),
    # half kneeling, back knee down, back foot up against a bench, front shin vertical;
    # the hips ease forward into the stretch and back
    'couch-stretch': dict(keys=[
        floor((0.49, 0.29), (0.50, 0.40), (0.50, 0.76), ((0.47, 0.68), (0.53, 0.68)),
              ((0.26, 0.78), (0.62, 0.955)), ((0.26, 0.955), (0.76, 0.80))),
        floor((0.46, 0.29), (0.47, 0.40), (0.46, 0.77), ((0.44, 0.68), (0.50, 0.68)),
              ((0.24, 0.79), (0.62, 0.955)), ((0.26, 0.955), (0.76, 0.80))),
    ], move=1.6, hold=0.6, props=[(0.76, 0.78, 0.96, 0.97)]),
    # front leg folded across, back leg long: chest upright, then hinged forward over the front leg
    'pigeon': dict(keys=[
        floor((0.465, 0.375), (0.48, 0.48), (0.56, 0.82), ((0.40, 0.76), (0.42, 0.76)),
              ((0.35, 0.90), (0.76, 0.92)), ((0.52, 0.945), (0.93, 0.95))),
        floor((0.19, 0.63), (0.30, 0.68), (0.56, 0.82), ((0.27, 0.955), (0.30, 0.955)),
              ((0.35, 0.90), (0.76, 0.92)), ((0.52, 0.945), (0.93, 0.95))),
    ], move=1.6, hold=0.8),
    # on the back, knees bent: hips down, then driven up and held at the top
    'glute-bridge': dict(keys=[
        floor((0.08, 0.895), (0.20, 0.90), (0.52, 0.93), ((0.42, 0.955), (0.44, 0.955)),
              ((0.68, 0.78), (0.70, 0.78)), ((0.76, 0.955), (0.78, 0.955))),
        floor((0.08, 0.895), (0.20, 0.90), (0.56, 0.77), ((0.42, 0.955), (0.44, 0.955)),
              ((0.74, 0.77), (0.76, 0.76)), ((0.76, 0.955), (0.78, 0.955))),
    ], move=1.0, hold=1.0),
}


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def blend(a, b, t):
    return {k: (a[k][0] + (b[k][0] - a[k][0]) * t, a[k][1] + (b[k][1] - a[k][1]) * t) for k in a}


def animate(keys, move=0.8, hold=0.25, loop=False, **draw_opts):
    """Frames for one cycle: pause on each key pose, ease to the next, end where it started."""
    path = keys + [keys[0]] if loop else keys + keys[-2::-1]
    frames, durations = [], []
    for a, b in zip(path, path[1:]):
        if hold > 0:
            frames.append(draw_pose(a, **draw_opts))
            durations.append(round(hold * 1000))
        n = max(2, round(move * FPS))
        for i in range(1, n):
            frames.append(draw_pose(blend(a, b, ease(i / n)), **draw_opts))
            durations.append(round(1000 / FPS))
    return frames, durations


def write(folder, name, spec):
    spec = dict(spec)
    frames, durations = animate(spec.pop('keys'), **spec)
    os.makedirs(folder, exist_ok=True)
    out = f"{folder}/{name}.webp"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0,
                   quality=80, method=4)
    print(f"wrote {out} ({len(frames)} frames, {os.path.getsize(out) // 1024} KB)")


if __name__ == '__main__':
    for name, spec in TAI_CHI.items():
        write('photos/tai-chi', name, spec)
    for name, spec in POSTURE.items():
        write('photos/posture', name, spec)
