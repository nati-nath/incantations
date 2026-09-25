"""Generate the 15 gym movement illustrations. Run: python3 make-illustrations.py

Simple original pictogram figures — not photos, not anyone's likeness — matching the app's own
dark/gold visual style (same palette as ../make-icon.py). Arms are a single straight capsule
from shoulder to hand (no elbow): two segments converging near the body's centre line — e.g.
hands clasped at the chest — draws an unavoidable "kite" shape with an elbow joint, so the
hand position alone has to carry each pose. Legs keep a knee joint since long straight legs
read fine and a squat needs the bend. Each pose is a small set of joint coordinates on a
normalised 0-1 grid (x: left->right, y: top->bottom).

Rerun this if you want to change a pose; movements.json's image paths don't need to change.
"""

from PIL import Image, ImageDraw

BG_TOP = (26, 31, 43)
BG_BOTTOM = (13, 15, 20)
GOLD = (217, 169, 76)

W, H = 640, 760  # squarish on purpose: a tall narrow canvas made the figure read as a thin skewer
SCALE = 3  # supersample then downscale for smooth anti-aliased lines


def bg(s_w, s_h):
    img = Image.new("RGB", (s_w, s_h))
    d = ImageDraw.Draw(img)
    for y in range(s_h):
        t = y / (s_h - 1)
        d.line([(0, y), (s_w, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)))
    return img, d


def capsule(d, p1, p2, w, r):
    d.line([p1, p2], fill=GOLD, width=w)
    for p in (p1, p2):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=GOLD)


def draw_pose(pose, ground=True):
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


def pose(**overrides):
    p = dict(BASE)
    p.update(overrides)
    return p


POSES = {
    # small hop, feet lifted off the ground, arms relaxed at the hips
    '01-lymphatic-hops': pose(
        l_hand=(0.38, 0.52), r_hand=(0.62, 0.52),
        l_knee=(0.45, 0.74), l_foot=(0.46, 0.88), r_knee=(0.55, 0.74), r_foot=(0.54, 0.88),
    ),
    # both arms reach straight overhead, torso curved into the wave
    '02-body-waves': pose(
        pelvis=(0.53, 0.57),
        l_hand=(0.34, -0.02), r_hand=(0.68, -0.02),
    ),
    # one arm swung up and back, the other forward and down
    '03-arm-swings': pose(
        l_hand=(0.26, 0.58),
        r_hand=(0.78, 0.02),
    ),
    # feet wide, hands crossed in front at chest height, shoulders rotated
    '04-trunk-twists': pose(
        l_foot=(0.30, 0.96), r_foot=(0.70, 0.96),
        l_shoulder=(0.44, 0.22), r_shoulder=(0.58, 0.25),
        l_hand=(0.62, 0.40), r_hand=(0.40, 0.42),
    ),
    # arms out to the sides, hands forward of the shoulders (mid-circle)
    '05-forward-arm-circles': pose(
        l_hand=(0.16, 0.30), r_hand=(0.84, 0.30),
    ),
    # deep knee bend, arms hanging straight for balance, feet wide
    '06-squats': pose(
        pelvis=(0.5, 0.68),
        l_hand=(0.40, 0.50), r_hand=(0.60, 0.50),
        l_knee=(0.38, 0.80), l_foot=(0.34, 0.96), r_knee=(0.62, 0.80), r_foot=(0.66, 0.96),
    ),
    # mirror of arm swings, opposite direction
    '07-backward-arm-swings': pose(
        l_hand=(0.22, 0.02),
        r_hand=(0.74, 0.58),
    ),
    # arms crossed over the chest, hands landing near the opposite shoulder
    '08-dead-arms': pose(
        l_hand=(0.58, 0.26),
        r_hand=(0.42, 0.28),
    ),
    # one arm raised high on the diagonal, the other swept low across the body
    '09-golf-swings': pose(
        pelvis=(0.46, 0.57),
        l_hand=(0.30, 0.56),
        r_hand=(0.80, -0.03),
    ),
    # right knee driven up high, opposite arm forward — mid-march. Hands stay on their own
    # side (never crossing the centre line) so the raised knee doesn't get lost in an X of limbs.
    '10-marches': pose(
        l_hand=(0.30, 0.28), r_hand=(0.70, 0.55),
        l_knee=(0.44, 0.77), l_foot=(0.42, 0.96),
        r_knee=(0.60, 0.42), r_foot=(0.58, 0.50),
    ),
    # up on the toes, both arms swinging overhead
    '11-tiptoe-arm-swings': pose(
        l_hand=(0.34, -0.03), r_hand=(0.66, -0.03),
        l_knee=(0.46, 0.75), l_foot=(0.46, 0.93), r_knee=(0.54, 0.75), r_foot=(0.54, 0.93),
    ),
    # one arm extended straight out to the side, torso twisted
    '12-twist-the-waist': pose(
        l_foot=(0.38, 0.96), r_foot=(0.62, 0.96),
        l_hand=(0.36, 0.52),
        r_hand=(0.90, 0.34),
    ),
    # arms wide (T shape), one leg stepped back into a small lunge
    '13-wide-arm-step-backs': pose(
        l_hand=(0.06, 0.28), r_hand=(0.94, 0.28),
        l_knee=(0.45, 0.75), l_foot=(0.46, 0.88), r_knee=(0.62, 0.85), r_foot=(0.72, 0.98),
    ),
    # lunge stance, both arms reaching up and over to one side
    '14-back-step-wave-lunges': pose(
        l_hand=(0.24, 0.00), r_hand=(0.56, -0.08),
        l_knee=(0.42, 0.74), l_foot=(0.42, 0.88), r_knee=(0.68, 0.86), r_foot=(0.80, 0.98),
    ),
    # wide plie stance, arms raised overhead and well apart
    '15-ballet-squats': pose(
        pelvis=(0.5, 0.66),
        l_hand=(0.32, -0.04), r_hand=(0.68, -0.04),
        l_knee=(0.32, 0.79), l_foot=(0.24, 0.96), r_knee=(0.68, 0.79), r_foot=(0.76, 0.96),
    ),
}

for name, p in POSES.items():
    draw_pose(p).save(f"photos/{name}.png")
    print(f"wrote photos/{name}.png")
