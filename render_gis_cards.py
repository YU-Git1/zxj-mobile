from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


SOURCE = Path(r"C:\Users\admin\AppData\Local\Temp\codex-clipboard-0c6c0819-e623-4f95-b49d-755bce084490.png")
OUTPUT_DIR = Path("output")
ASSET_DIR = OUTPUT_DIR / "gis-assets"
BASEMAP = ASSET_DIR / "shanghai-aerial.png"
COMPOSITE = OUTPUT_DIR / "zaoxingjia-gis-scenes-v2.png"

WIDTH = 1536
HEIGHT = 864
CYAN = (0, 222, 236)
CYAN_SOFT = (43, 174, 193)
AMBER = (255, 170, 58)
RED = (255, 86, 77)
GREEN = (86, 224, 145)


def color_grade(image: Image.Image, brightness: float = 0.56) -> Image.Image:
    image = ImageEnhance.Color(image.convert("RGB")).enhance(0.72)
    image = ImageEnhance.Contrast(image).enhance(1.18)
    image = ImageEnhance.Brightness(image).enhance(brightness).convert("RGBA")
    tint = Image.new("RGBA", image.size, (0, 30, 34, 58))
    image.alpha_composite(tint)

    vignette = Image.new("L", image.size, 0)
    vignette_draw = ImageDraw.Draw(vignette)
    vignette_draw.ellipse((-260, -320, WIDTH + 260, HEIGHT + 360), fill=205)
    vignette = vignette.filter(ImageFilter.GaussianBlur(150))
    shade = Image.new("RGBA", image.size, (0, 7, 9, 0))
    shade.putalpha(Image.eval(vignette, lambda value: 180 - int(value * 0.70)))
    image.alpha_composite(shade)
    return image


def add_frame(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((18, 18, WIDTH - 19, HEIGHT - 19), outline=(*CYAN_SOFT, 70), width=2)
    length = 72
    inset = 36
    for x, y, sx, sy in (
        (inset, inset, 1, 1),
        (WIDTH - inset, inset, -1, 1),
        (inset, HEIGHT - inset, 1, -1),
        (WIDTH - inset, HEIGHT - inset, -1, -1),
    ):
        draw.line((x, y, x + sx * length, y), fill=(*CYAN, 185), width=4)
        draw.line((x, y, x, y + sy * length), fill=(*CYAN, 185), width=4)


def add_grid(draw: ImageDraw.ImageDraw, alpha: int = 28) -> None:
    for x in range(0, WIDTH, 96):
        draw.line((x, 0, x, HEIGHT), fill=(*CYAN_SOFT, alpha), width=1)
    for y in range(0, HEIGHT, 96):
        draw.line((0, y, WIDTH, y), fill=(*CYAN_SOFT, alpha), width=1)


def ai_recognition(base: Image.Image) -> Image.Image:
    scene = color_grade(base, 0.63)
    overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    add_grid(draw, 17)

    buildings = [
        [(913, 180), (985, 161), (1023, 198), (946, 222)],
        [(1072, 201), (1159, 183), (1201, 229), (1114, 251)],
        [(1195, 300), (1278, 279), (1332, 328), (1244, 350)],
        [(1000, 338), (1091, 312), (1134, 353), (1040, 383)],
        [(820, 362), (900, 335), (955, 381), (874, 411)],
        [(671, 475), (752, 446), (805, 492), (716, 523)],
        [(1128, 471), (1206, 446), (1251, 491), (1168, 518)],
        [(1245, 538), (1336, 514), (1380, 555), (1290, 586)],
        [(917, 594), (1004, 567), (1053, 610), (963, 640)],
        [(764, 649), (842, 619), (891, 660), (808, 693)],
    ]
    for index, polygon in enumerate(buildings):
        color = AMBER if index == 4 else CYAN
        draw.polygon(polygon, fill=(*color, 43), outline=(*color, 220))
        for px, py in polygon:
            draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(*color, 240))

    scan_y = 410
    draw.rectangle((0, scan_y - 28, WIDTH, scan_y + 28), fill=(*CYAN, 10))
    draw.rectangle((0, scan_y - 2, WIDTH, scan_y + 2), fill=(*CYAN, 145))
    for x in range(70, WIDTH - 70, 34):
        draw.ellipse((x - 2, scan_y - 2, x + 2, scan_y + 2), fill=(*CYAN, 230))

    focus = buildings[4]
    xs = [point[0] for point in focus]
    ys = [point[1] for point in focus]
    x0, x1 = min(xs) - 22, max(xs) + 22
    y0, y1 = min(ys) - 22, max(ys) + 22
    draw.rectangle((x0, y0, x1, y1), outline=(*AMBER, 190), width=3)
    draw.line((x0, y0, x0 + 34, y0), fill=(*AMBER, 255), width=7)
    draw.line((x0, y0, x0, y0 + 34), fill=(*AMBER, 255), width=7)
    draw.line((x1, y1, x1 - 34, y1), fill=(*AMBER, 255), width=7)
    draw.line((x1, y1, x1, y1 - 34), fill=(*AMBER, 255), width=7)

    add_frame(draw)
    glow = overlay.filter(ImageFilter.GaussianBlur(18))
    glow.putalpha(glow.getchannel("A").point(lambda value: int(value * 0.32)))
    scene.alpha_composite(glow)
    scene.alpha_composite(overlay)
    return scene


def perspective_basemap(base: Image.Image) -> Image.Image:
    source = color_grade(base, 0.50)
    transformed = source.transform(
        (WIDTH, HEIGHT),
        Image.Transform.PERSPECTIVE,
        (1.16, 0.15, -118, 0.0, 1.02, -26, 0.00003, 0.00042),
        resample=Image.Resampling.BICUBIC,
    )
    sky = Image.new("RGBA", transformed.size, (5, 18, 21, 255))
    mask = Image.new("L", transformed.size, 255)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rectangle((0, 0, WIDTH, 158), fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(42))
    sky.paste(transformed, (0, 0), mask)
    return sky


def prism(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, d: int, h: int, accent: tuple[int, int, int]) -> None:
    top = [(x, y - h), (x + w, y - h - d), (x + w + d, y - h), (x + d, y - h + d)]
    left = [(x, y - h), (x + d, y - h + d), (x + d, y + d), (x, y)]
    right = [(x + d, y - h + d), (x + w + d, y - h), (x + w + d, y), (x + d, y + d)]
    draw.polygon(left, fill=(12, 67, 75, 218), outline=(*accent, 185))
    draw.polygon(right, fill=(19, 86, 95, 224), outline=(*accent, 185))
    draw.polygon(top, fill=(41, 119, 128, 235), outline=(*accent, 235))
    for floor_y in range(y - h + 18, y, 22):
        draw.line((x, floor_y, x + d, floor_y + d), fill=(*accent, 70), width=1)
        draw.line((x + d, floor_y + d, x + w + d, floor_y), fill=(*accent, 64), width=1)


def site_reconstruction(base: Image.Image) -> Image.Image:
    scene = perspective_basemap(base)
    overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    vanishing = (768, 165)
    for x in range(-600, WIDTH + 700, 110):
        draw.line((x, HEIGHT, vanishing[0], vanishing[1]), fill=(*CYAN_SOFT, 44), width=2)
    for y in (330, 430, 520, 610, 700, 790):
        draw.line((0, y, WIDTH, y), fill=(*CYAN_SOFT, 28), width=2)

    prisms = [
        (232, 627, 120, 35, 154),
        (385, 693, 170, 44, 236),
        (610, 650, 125, 36, 184),
        (800, 721, 190, 48, 298),
        (1078, 651, 128, 38, 202),
        (1256, 708, 108, 34, 262),
    ]
    for index, values in enumerate(prisms):
        prism(draw, *values, AMBER if index == 3 else CYAN)

    for x, y, _, _, h in prisms:
        draw.ellipse((x - 4, y - h - 4, x + 4, y - h + 4), fill=(*CYAN, 225))
    draw.line((90, 760, 1450, 760), fill=(*CYAN, 90), width=2)
    draw.rectangle((101, 91, 438, 105), fill=(*CYAN, 35))
    draw.rectangle((101, 91, 322, 105), fill=(*CYAN, 210))
    for x in range(101, 439, 42):
        draw.line((x, 84, x, 112), fill=(*CYAN, 95), width=1)
    add_frame(draw)

    glow = overlay.filter(ImageFilter.GaussianBlur(16))
    glow.putalpha(glow.getchannel("A").point(lambda value: int(value * 0.24)))
    scene.alpha_composite(glow)
    scene.alpha_composite(overlay)
    return scene


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: tuple[int, int, int]) -> None:
    draw.line((*start, *end), fill=(*color, 255), width=8)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 24
    points = [
        end,
        (end[0] - size * math.cos(angle - 0.48), end[1] - size * math.sin(angle - 0.48)),
        (end[0] - size * math.cos(angle + 0.48), end[1] - size * math.sin(angle + 0.48)),
    ]
    draw.polygon(points, fill=(*color, 255))


def manual_adjustment(base: Image.Image) -> Image.Image:
    scene = perspective_basemap(base)
    overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    vanishing = (758, 160)
    for x in range(-500, WIDTH + 600, 128):
        draw.line((x, HEIGHT, vanishing[0], vanishing[1]), fill=(*CYAN_SOFT, 34), width=2)
    for y in (390, 500, 610, 720, 815):
        draw.line((0, y, WIDTH, y), fill=(*CYAN_SOFT, 26), width=2)

    prism(draw, 365, 705, 168, 43, 222, CYAN)
    prism(draw, 660, 680, 210, 52, 292, AMBER)
    prism(draw, 1060, 714, 135, 37, 188, CYAN)

    center = (791, 540)
    draw.ellipse((center[0] - 173, center[1] - 70, center[0] + 173, center[1] + 70), outline=(*CYAN, 160), width=5)
    draw.arc((center[0] - 126, center[1] - 126, center[0] + 126, center[1] + 126), 202, 535, fill=(*AMBER, 235), width=6)
    for angle in (30, 150, 270):
        px = center[0] + int(math.cos(math.radians(angle)) * 126)
        py = center[1] + int(math.sin(math.radians(angle)) * 126)
        draw.rectangle((px - 7, py - 7, px + 7, py + 7), fill=(*AMBER, 255))

    arrow(draw, center, (1000, 541), RED)
    arrow(draw, center, (650, 655), GREEN)
    arrow(draw, center, (791, 283), CYAN)
    draw.ellipse((center[0] - 13, center[1] - 13, center[0] + 13, center[1] + 13), fill=(235, 247, 248, 255))

    box = (620, 323, 984, 743)
    draw.rectangle(box, outline=(*AMBER, 210), width=3)
    for x, y in ((box[0], box[1]), (box[2], box[1]), (box[0], box[3]), (box[2], box[3])):
        draw.rectangle((x - 8, y - 8, x + 8, y + 8), fill=(*AMBER, 255))
    draw.line((117, 116, 117, 241), fill=(*CYAN, 160), width=3)
    for y, width in ((116, 178), (158, 244), (200, 132), (241, 210)):
        draw.rectangle((117, y - 4, 117 + width, y + 4), fill=(*CYAN_SOFT, 80))
        draw.rectangle((117, y - 4, 117 + int(width * 0.68), y + 4), fill=(*CYAN, 175))
    add_frame(draw)

    glow = overlay.filter(ImageFilter.GaussianBlur(18))
    glow.putalpha(glow.getchannel("A").point(lambda value: int(value * 0.25)))
    scene.alpha_composite(glow)
    scene.alpha_composite(overlay)
    return scene


def detect_placeholders(source: Image.Image) -> list[tuple[int, int, int, int]]:
    rgb = np.asarray(source.convert("RGB"))
    spread = rgb.max(axis=2) - rgb.min(axis=2)
    luminance = rgb.mean(axis=2)
    mask = (spread <= 3) & (luminance >= 75) & (luminance <= 105)
    boxes: list[tuple[int, int, int, int]] = []
    active: dict[tuple[int, int], tuple[int, int]] = {}
    for y in range(mask.shape[0]):
        row = mask[y]
        changes = np.diff(np.pad(row.astype(np.int8), (1, 1)))
        runs = {
            (int(start), int(end))
            for start, end in zip(np.flatnonzero(changes == 1), np.flatnonzero(changes == -1))
            if end - start > 300
        }
        for run in list(active):
            if run not in runs:
                start_y, last_y = active.pop(run)
                if last_y - start_y > 150:
                    boxes.append((run[0], start_y, run[1], last_y + 1))
        for run in runs:
            start_y, _ = active.get(run, (y, y))
            active[run] = (start_y, y)
    return sorted(boxes, key=lambda box: box[0])


def rounded_asset(scene: Image.Image, size: tuple[int, int], radius: int = 4) -> Image.Image:
    fitted = scene.resize(size, Image.Resampling.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    fitted.putalpha(mask)
    return fitted


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    basemap = Image.open(BASEMAP).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    scenes = [ai_recognition(basemap), site_reconstruction(basemap), manual_adjustment(basemap)]
    names = ["ai-building-recognition.png", "site-reconstruction.png", "manual-adjustment.png"]
    for scene, name in zip(scenes, names):
        scene.convert("RGB").save(ASSET_DIR / name, quality=96, optimize=True)

    source = Image.open(SOURCE).convert("RGBA")
    boxes = detect_placeholders(source)
    if len(boxes) != 3:
        raise RuntimeError(f"Expected 3 placeholders, found {len(boxes)}: {boxes}")
    for scene, (x0, y0, x1, y1) in zip(scenes, boxes):
        source.alpha_composite(rounded_asset(scene, (x1 - x0, y1 - y0)), (x0, y0))
    source.convert("RGB").save(COMPOSITE, quality=96, optimize=True)
    print(f"Placeholders: {boxes}")
    print(COMPOSITE.resolve())


if __name__ == "__main__":
    main()
