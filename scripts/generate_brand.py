"""Generate Home Assistant brand images for Kocom Smart Home+ Energy.

The artwork is an original geometric brand mark on a dark navy rounded square:
a centered cyan and white smart wallpad screen displaying a golden energy
lightning bolt and meter bars. It does not reuse any manufacturer trademark.
Drawn from geometric primitives at 4x scale and downsampled, so no source image,
external font file, or network access is needed. Run with Pillow 12.3.0 for
reproducible PNGs.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BRAND = Path(__file__).resolve().parents[1] / "custom_components/kocom_smarthome/brand"
SIZE = 512
SCALE = 4
NAVY = "#1b2a41"
CYAN = "#18bcf2"
WHITE = "#ffffff"
YELLOW = "#ffd23f"
GOLD = "#f2a900"
GREEN = "#34d399"
WORDMARK = "#18bcf2"


def _rounded_polygon(
    points: list[tuple[float, float]],
    radii: list[float] | float,
    steps: int = 24,
) -> list[tuple[float, float]]:
    """Return polygon vertices with mathematically rounded corners."""
    n = len(points)
    if isinstance(radii, (int, float)):
        radii = [float(radii)] * n
    poly_pts: list[tuple[float, float]] = []
    for i in range(n):
        r = radii[i]
        if r <= 0:
            poly_pts.append(points[i])
            continue
        p_prev = points[(i - 1) % n]
        p_curr = points[i]
        p_next = points[(i + 1) % n]

        v1 = (p_prev[0] - p_curr[0], p_prev[1] - p_curr[1])
        v2 = (p_next[0] - p_curr[0], p_next[1] - p_curr[1])
        l1 = math.hypot(*v1)
        l2 = math.hypot(*v2)
        u1 = (v1[0] / l1, v1[1] / l1)
        u2 = (v2[0] / l2, v2[1] / l2)

        dot = max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))
        half_ang = math.acos(dot) / 2.0
        dist = min(r / math.tan(half_ang), l1 * 0.45, l2 * 0.45)
        eff_r = dist * math.tan(half_ang)
        t1 = (p_curr[0] + u1[0] * dist, p_curr[1] + u1[1] * dist)
        t2 = (p_curr[0] + u2[0] * dist, p_curr[1] + u2[1] * dist)

        bis = (u1[0] + u2[0], u1[1] + u2[1])
        bl = math.hypot(*bis)
        ub = (bis[0] / bl, bis[1] / bl)
        c_dist = eff_r / math.sin(half_ang)
        center = (p_curr[0] + ub[0] * c_dist, p_curr[1] + ub[1] * c_dist)

        a1 = math.atan2(t1[1] - center[1], t1[0] - center[0])
        a2 = math.atan2(t2[1] - center[1], t2[0] - center[0])
        da = a2 - a1
        while da <= -math.pi:
            da += 2 * math.pi
        while da > math.pi:
            da -= 2 * math.pi

        for s_idx in range(steps + 1):
            a = a1 + da * s_idx / steps
            poly_pts.append(
                (center[0] + eff_r * math.cos(a), center[1] + eff_r * math.sin(a))
            )
    return poly_pts


def draw_icon() -> Image.Image:
    """Draw the 512px RGBA app icon."""
    s = SCALE
    image = Image.new("RGBA", (SIZE * s, SIZE * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(image)

    def box(x0: float, y0: float, x1: float, y1: float) -> list[float]:
        return [x0 * s, y0 * s, x1 * s, y1 * s]

    # 1. Dark navy rounded square background.
    d.rounded_rectangle(box(0, 0, SIZE - 1, SIZE - 1), radius=104 * s, fill=NAVY)

    # 2. Centered Smart Wallpad outer body (white) and cyan screen bezel.
    d.rounded_rectangle(box(88, 76, 424, 436), radius=44 * s, fill=WHITE)
    d.rounded_rectangle(box(114, 102, 398, 372), radius=26 * s, fill=CYAN)
    d.rounded_rectangle(box(130, 118, 382, 356), radius=18 * s, fill=NAVY)

    # Wallpad touch home button at bottom center of the white frame.
    d.ellipse(box(238, 386, 274, 422), fill=NAVY)
    d.ellipse(box(246, 394, 266, 414), fill=CYAN)

    # 3. Golden Energy Lightning Bolt inside the wallpad screen.
    bolt_pts = [
        (250 * s, 142 * s),
        (164 * s, 246 * s),
        (220 * s, 246 * s),
        (196 * s, 334 * s),
        (290 * s, 224 * s),
        (234 * s, 224 * s),
    ]
    d.polygon(_rounded_polygon(bolt_pts, 6 * s), fill=YELLOW)

    # 4. Utility meter bars (electricity/gas/water/heat) on the right side of the screen.
    d.rounded_rectangle(box(306, 160, 354, 180), radius=6 * s, fill=GOLD)
    d.rounded_rectangle(box(306, 198, 354, 218), radius=6 * s, fill=CYAN)
    d.rounded_rectangle(box(306, 236, 354, 256), radius=6 * s, fill=GREEN)
    d.rounded_rectangle(box(306, 274, 354, 294), radius=6 * s, fill=WHITE)

    return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main() -> None:
    """Write icon.png, icon@2x.png, logo.png and logo@2x.png."""
    BRAND.mkdir(parents=True, exist_ok=True)
    icon = draw_icon()
    icon.save(BRAND / "icon@2x.png", optimize=True)
    icon.resize((256, 256), Image.Resampling.LANCZOS).save(
        BRAND / "icon.png", optimize=True
    )

    # Pillow bundles Aileron Regular, so regeneration needs no system fonts.
    font = ImageFont.load_default(size=416)
    bounds = font.getbbox("Kocom")
    wordmark = Image.new("RGBA", (bounds[2] - bounds[0], bounds[3] - bounds[1]))
    ImageDraw.Draw(wordmark).text(
        (-bounds[0], -bounds[1]), "Kocom", font=font, fill=WORDMARK
    )
    wordmark = wordmark.crop(wordmark.getbbox())
    gap = 96 + ((SIZE + 96 + wordmark.width) % 2)
    logo = Image.new("RGBA", (SIZE + gap + wordmark.width, SIZE))
    logo.alpha_composite(icon, (0, 0))
    logo.alpha_composite(wordmark, (SIZE + gap, (SIZE - wordmark.height) // 2))
    logo = logo.crop(logo.getbbox())
    logo.save(BRAND / "logo@2x.png", optimize=True)
    logo.resize((logo.width // 2, logo.height // 2), Image.Resampling.LANCZOS).save(
        BRAND / "logo.png", optimize=True
    )


if __name__ == "__main__":
    main()
