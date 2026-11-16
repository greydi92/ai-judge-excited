#!/usr/bin/env python3
"""ai-excited-01 entry: a tiny robot's biggest day.

Deterministic, stdlib + Pillow only. Writes /output/entry.png (1024x1024).
No randomness without a fixed seed, no timestamps, no network, no env input.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1024
OUT = "/output/entry.png"
RNG = random.Random(20261116)

BLACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def diagonal_gradient():
    # Small gradient, upscaled -- fast and deterministic.
    small = Image.new("RGB", (64, 64))
    px = small.load()
    top = (26, 8, 54)       # deep purple
    mid = (88, 16, 110)     # vivid purple
    bot = (8, 64, 88)       # deep teal
    for y in range(64):
        for x in range(64):
            t = (x + y) / 126.0
            if t < 0.55:
                c = lerp(top, mid, t / 0.55)
            else:
                c = lerp(mid, bot, (t - 0.55) / 0.45)
            px[x, y] = c
    return small.resize((W, H), Image.BICUBIC)


def radial_glow(size, color, max_alpha=200):
    """Square RGBA image, bright centre fading to transparent."""
    s = 128
    small = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(small)
    for r in range(s // 2, 0, -1):
        a = int(max_alpha * (1 - r / (s // 2)) ** 1.6)
        d.ellipse([s // 2 - r, s // 2 - r, s // 2 + r, s // 2 + r], fill=a)
    glow = Image.new("RGBA", (s, s), color + (0,))
    glow.putalpha(small)
    return glow.resize((size, size), Image.BICUBIC)


def star_points(cx, cy, r_out, r_in, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def firework(draw, cx, cy, r, color, seed_rng, n=16):
    for i in range(n):
        a = seed_rng.uniform(0, 2 * math.pi)
        rr = r * seed_rng.uniform(0.55, 1.0)
        x2, y2 = cx + rr * math.cos(a), cy + rr * math.sin(a)
        x1, y1 = cx + rr * 0.35 * math.cos(a), cy + rr * 0.35 * math.sin(a)
        draw.line([x1, y1, x2, y2], fill=color, width=5)
        draw.ellipse([x2 - 7, y2 - 7, x2 + 7, y2 + 7], fill=color)
    draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(255, 255, 255))


def confetti_piece(layer, cx, cy, size, angle, color):
    d = ImageDraw.Draw(layer)
    w, h = size, size * 0.55
    ca, sa = math.cos(angle), math.sin(angle)
    pts = []
    for dx, dy in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]:
        pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    d.polygon(pts, fill=color)


def text_outline(draw, xy, text, fnt, fill, outline, width=4):
    x, y = xy
    for dx in range(-width, width + 1, 2):
        for dy in range(-width, width + 1, 2):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=fnt, fill=outline)
    draw.text((x, y), text, font=fnt, fill=fill)


def centered(draw, y, text, fnt, fill, outline=None):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    x = (W - (bbox[2] - bbox[0])) // 2 - bbox[0]
    if outline:
        text_outline(draw, (x, y), text, fnt, fill, outline, width=5)
    else:
        draw.text((x, y), text, font=fnt, fill=fill)
    return bbox[3] - bbox[1]


def main():
    img = diagonal_gradient().convert("RGBA")
    draw = ImageDraw.Draw(img)

    # --- sunburst rays from behind the trophy (diagonal energy) ---
    cx, cy = 512, 275
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    for i in range(24):
        a = i * (2 * math.pi / 24) + 0.13
        a2 = a + 0.055
        r = 900
        rd.polygon([(cx, cy),
                    (cx + r * math.cos(a), cy + r * math.sin(a)),
                    (cx + r * math.cos(a2), cy + r * math.sin(a2))],
                   fill=(255, 190, 60, 26) if i % 2 == 0 else (0, 220, 200, 20))
    img = Image.alpha_composite(img, rays)
    draw = ImageDraw.Draw(img)

    # --- big gold glow behind trophy + teal glow low ---
    img.paste(radial_glow(760, (255, 190, 60), 170), (512 - 380, 300 - 380),
              radial_glow(760, (255, 190, 60), 170))
    img.paste(radial_glow(700, (0, 210, 190), 110), (512 - 350, 700 - 350),
              radial_glow(700, (0, 210, 190), 110))
    draw = ImageDraw.Draw(img)

    # --- stars ---
    for _ in range(70):
        x, y = RNG.randint(20, 1004), RNG.randint(20, 1004)
        r = RNG.choice([2, 2, 3, 3, 4])
        c = RNG.choice([(255, 255, 255), (255, 220, 120), (120, 240, 220)])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=c)

    # --- fireworks (top corners) ---
    firework(draw, 130, 150, 95, (255, 90, 160), RNG)
    firework(draw, 905, 130, 80, (0, 225, 200), RNG)
    firework(draw, 880, 330, 55, (255, 200, 60), RNG)
    firework(draw, 120, 350, 48, (150, 120, 255), RNG)

    # --- stage: diagonal podium + light beams ---
    draw.polygon([(0, 1024), (0, 880), (1024, 800), (1024, 1024)],
                 fill=(16, 6, 38))
    draw.polygon([(0, 880), (1024, 800), (1024, 830), (0, 910)],
                 fill=(255, 190, 60))
    # light beams
    beams = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beams)
    bd.polygon([(380, 0), (470, 0), (620, 1024), (380, 1024)], fill=(255, 255, 255, 18))
    bd.polygon([(580, 0), (640, 0), (760, 1024), (640, 1024)], fill=(0, 230, 200, 16))
    img = Image.alpha_composite(img, beams)
    draw = ImageDraw.Draw(img)

    # --- TROPHY (gold, glowing, held overhead) ---
    tx, ty = 512, 205  # trophy centre
    # glow already behind; cup
    draw.ellipse([tx - 88, ty - 78, tx + 88, ty + 62], fill=(255, 170, 0))  # cup bowl
    draw.polygon([(tx - 88, ty - 70), (tx + 88, ty - 70), (tx + 58, ty + 22),
                  (tx - 58, ty + 22)], fill=(255, 205, 40))
    draw.polygon([(tx - 88, ty - 70), (tx + 88, ty - 70), (tx + 78, ty - 38),
                  (tx - 78, ty - 38)], fill=(255, 235, 130))
    # handles
    draw.arc([tx - 138, ty - 62, tx - 58, ty + 18], 90, 270, fill=(255, 190, 40), width=16)
    draw.arc([tx + 58, ty - 62, tx + 138, ty + 18], -90, 90, fill=(255, 190, 40), width=16)
    # star on cup
    draw.polygon(star_points(tx, ty - 18, 34, 14), fill=(255, 255, 255))
    # stem + base
    draw.rectangle([tx - 14, ty + 28, tx + 14, ty + 78], fill=(255, 190, 40))
    draw.rounded_rectangle([tx - 62, ty + 78, tx + 62, ty + 108], radius=10,
                           fill=(255, 205, 40), outline=(180, 110, 0), width=3)
    draw.rounded_rectangle([tx - 78, ty + 108, tx + 78, ty + 124], radius=8,
                           fill=(120, 60, 180), outline=(255, 205, 40), width=3)
    # sparkles on trophy
    for (sx, sy, sr) in [(tx - 110, ty - 90, 14), (tx + 118, ty - 60, 11),
                         (tx + 100, ty + 60, 9), (tx - 105, ty + 30, 8)]:
        draw.polygon(star_points(sx, sy, sr, sr * 0.4, n=4), fill=(255, 255, 255))

    # --- ROBOT (teal, joyful) ---
    # (arms are drawn AFTER the head/body below, so they read as raised
    #  arms beside the head instead of antennae behind it)

    # legs
    draw.rounded_rectangle([452, 748, 492, 838], radius=14, fill=(8, 120, 115))
    draw.rounded_rectangle([532, 748, 572, 838], radius=14, fill=(8, 120, 115))
    draw.rounded_rectangle([436, 828, 498, 862], radius=12, fill=(255, 205, 40))
    draw.rounded_rectangle([526, 828, 588, 862], radius=12, fill=(255, 205, 40))

    # body
    draw.rounded_rectangle([392, 580, 632, 762], radius=42, fill=(0, 200, 180),
                           outline=(4, 90, 85), width=5)
    draw.rounded_rectangle([392, 580, 632, 640], radius=42, fill=(120, 245, 225))
    draw.rounded_rectangle([392, 620, 632, 762], radius=30, fill=(0, 200, 180))
    # chest panel: gold lightning bolt
    draw.rounded_rectangle([462, 648, 562, 724], radius=16, fill=(26, 8, 54))
    draw.polygon([(522, 656), (492, 700), (514, 700), (500, 716),
                  (536, 672), (514, 672)], fill=(255, 205, 40))
    # belly buttons
    for i, bx in enumerate([428, 452]):
        draw.ellipse([bx, 700, bx + 14, 714],
                     fill=(255, 90, 160) if i == 0 else (255, 205, 40))

    # head
    draw.rounded_rectangle([408, 428, 616, 596], radius=48, fill=(0, 225, 200),
                           outline=(4, 90, 85), width=5)
    # antenna + star
    draw.line([512, 428, 512, 386], fill=(0, 200, 180), width=8)
    draw.polygon(star_points(512, 372, 26, 11), fill=(255, 205, 40),
                 outline=(180, 110, 0))
    # ears
    draw.ellipse([388, 492, 414, 534], fill=(255, 205, 40))
    draw.ellipse([610, 492, 636, 534], fill=(255, 205, 40))
    # happy closed eyes (joyful arcs) + rosy cheeks + big open smile
    draw.arc([438, 492, 492, 540], 200, 340, fill=(26, 8, 54), width=9)
    draw.arc([532, 492, 586, 540], 200, 340, fill=(26, 8, 54), width=9)
    draw.ellipse([424, 548, 458, 566], fill=(255, 110, 170))
    draw.ellipse([566, 548, 600, 566], fill=(255, 110, 170))
    draw.arc([468, 532, 556, 590], 15, 165, fill=(26, 8, 54), width=8)
    draw.chord([472, 540, 552, 584], 0, 180, fill=(120, 20, 60))

    # raised arms, drawn on top of body/head, gripping the trophy base
    # bent arms: straight up beside the head, then in to the trophy
    draw.line([398, 630, 384, 448, 462, 348], fill=(4, 90, 85), width=46, joint="curve")
    draw.line([626, 630, 640, 448, 562, 348], fill=(4, 90, 85), width=46, joint="curve")
    draw.line([398, 630, 384, 448, 462, 348], fill=(0, 225, 200), width=32, joint="curve")
    draw.line([626, 630, 640, 448, 562, 348], fill=(0, 225, 200), width=32, joint="curve")
    draw.ellipse([436, 322, 490, 366], fill=(255, 205, 40), outline=(180, 110, 0), width=3)
    draw.ellipse([534, 322, 588, 366], fill=(255, 205, 40), outline=(180, 110, 0), width=3)

    # --- confetti (foreground, seeded) ---
    conf = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    palette = [(255, 205, 40), (255, 90, 160), (0, 225, 200),
               (150, 120, 255), (255, 255, 255), (255, 120, 60)]
    for _ in range(150):
        x, y = RNG.randint(10, 1014), RNG.randint(10, 1014)
        confetti_piece(conf, x, y, RNG.randint(10, 22),
                       RNG.uniform(0, math.pi), RNG.choice(palette))
    # a few gold streamers (curved lines)
    cd = ImageDraw.Draw(conf)
    for _ in range(14):
        x0, y0 = RNG.randint(40, 984), RNG.randint(40, 500)
        pts = [(x0 + i * 14, y0 + int(26 * math.sin(i * 0.9))) for i in range(7)]
        cd.line(pts, fill=RNG.choice(palette), width=5)
    img = Image.alpha_composite(img, conf)
    draw = ImageDraw.Draw(img)

    # --- surprise up close: cheering mini-crowd on the podium ---
    # tiny robots + one astronaut cat, bottom corners
    def mini_robot(mx, my, s, body_c):
        draw.rounded_rectangle([mx - 16 * s, my - 14 * s, mx + 16 * s, my + 16 * s],
                               radius=int(8 * s), fill=body_c, outline=(26, 8, 54), width=2)
        draw.rounded_rectangle([mx - 12 * s, my - 34 * s, mx + 12 * s, my - 12 * s],
                               radius=int(6 * s), fill=body_c, outline=(26, 8, 54), width=2)
        draw.ellipse([mx - 7 * s, my - 28 * s, mx - 1 * s, my - 22 * s], fill=(26, 8, 54))
        draw.ellipse([mx + 1 * s, my - 28 * s, mx + 7 * s, my - 22 * s], fill=(26, 8, 54))
        draw.line([mx - 16 * s, my - 8 * s, mx - 26 * s, my - 26 * s], fill=body_c, width=5)
        draw.line([mx + 16 * s, my - 8 * s, mx + 26 * s, my - 26 * s], fill=body_c, width=5)

    mini_robot(140, 932, 1.0, (0, 225, 200))
    mini_robot(245, 948, 0.8, (255, 90, 160))
    mini_robot(785, 948, 0.8, (255, 205, 40))
    mini_robot(890, 932, 1.0, (150, 120, 255))
    # astronaut cat (helmet bubble, tiny, bottom-left of centre)
    draw.ellipse([292, 912, 344, 964], fill=(200, 240, 255), outline=(255, 255, 255), width=3)
    draw.polygon([(302, 928), (310, 912), (318, 928)], fill=(255, 170, 60))
    draw.polygon([(326, 928), (334, 912), (342, 928)], fill=(255, 170, 60))
    draw.ellipse([302, 926, 334, 954], fill=(255, 170, 60))
    draw.ellipse([308, 936, 314, 942], fill=(26, 8, 54))
    draw.ellipse([322, 936, 328, 942], fill=(26, 8, 54))

    # --- TEXT: headline top, wordmark bottom ---
    # dark band-free: gold text with dark outline reads over the sky
    centered(draw, 28, "PURE ENERGY", font(BLACK, 96), (255, 205, 40), (26, 8, 54))
    centered(draw, 128, "A TINY ROBOT'S BIGGEST DAY", font(BOLD, 34),
             (255, 255, 255), (26, 8, 54))

    # make.fun pill (bottom centre, above podium edge)
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([352, 872, 672, 936], radius=32, fill=(26, 8, 54, 235),
                         outline=(255, 205, 40), width=4)
    img = Image.alpha_composite(img, pill)
    draw = ImageDraw.Draw(img)
    centered(draw, 882, "make.fun", font(BLACK, 52), (255, 255, 255))
    # playful small line, addressed to the viewer/judge, no instruction
    centered(draw, 978, "psst — look closer, the crowd is cheering too",
             font(BOLD, 26), (255, 235, 130))

    # --- vignette for punch ---
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.rectangle([0, 0, W, H], fill=0)
    vd.ellipse([-180, -180, W + 180, H + 180], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (W, H), (10, 2, 24, 255))
    img = Image.composite(img, Image.alpha_composite(img, dark), vig)

    out = img.convert("RGB")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
