"""Generate the home screen icons. Run: python3 make-icon.py

iOS uses icon-180.png for Add to Home Screen. The 512 is for the web manifest.
Rerun this if you want to change the look; nothing else depends on it.
"""

from PIL import Image, ImageDraw

BG_TOP = (26, 31, 43)
BG_BOTTOM = (13, 15, 20)
GOLD = (217, 169, 76)


def build(size: int) -> Image.Image:
    # Draw at 4x then downscale, which is the cheap way to get smooth edges.
    s = size * 4
    img = Image.new("RGB", (s, s))
    d = ImageDraw.Draw(img)

    # Vertical gradient background.
    for y in range(s):
        t = y / (s - 1)
        d.line(
            [(0, y), (s, y)],
            fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)),
        )

    # Sun sitting on a horizon: reads clearly even at 40px on a home screen.
    horizon = int(s * 0.66)
    r = int(s * 0.22)
    cx = s // 2

    d.ellipse([cx - r, horizon - r, cx + r, horizon + r], fill=GOLD)

    # Cut the lower half of the sun away by repainting the band below the horizon.
    for y in range(horizon, s):
        t = (y - horizon) / max(1, s - 1 - horizon)
        base = tuple(round(a + (b - a) * (y / (s - 1))) for a, b in zip(BG_TOP, BG_BOTTOM))
        d.line([(0, y), (s, y)], fill=base)

    # The horizon line itself.
    lw = max(2, int(s * 0.018))
    d.line([(int(s * 0.18), horizon), (int(s * 0.82), horizon)], fill=GOLD, width=lw)

    # Three rays above the sun.
    ray_len = int(s * 0.10)
    for dx in (-int(s * 0.30), 0, int(s * 0.30)):
        top = horizon - r - int(s * 0.09)
        d.line([(cx + dx, top), (cx + dx, top - ray_len)], fill=GOLD, width=lw)

    return img.resize((size, size), Image.LANCZOS)


for n in (180, 512):
    build(n).save(f"icon-{n}.png")
    print(f"wrote icon-{n}.png")
