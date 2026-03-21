"""图片生成模块：在线 API 出图 + Pillow 程序化兜底"""

import io
import random
import logging
import httpx
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


async def generate_lantern_image_api(beautified_text: str, theme: str, config: dict) -> bytes:
    """调用 SiliconFlow FLUX.1-schnell 生成天灯图片，返回 PNG bytes"""
    img_cfg = config["image_api"]
    theme_en = config["themes"].get(theme, {}).get("en", "peaceful")
    prompt = img_cfg["prompt_template"].format(theme_en=theme_en)

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{img_cfg['base_url']}/images/generations",
            headers={
                "Authorization": f"Bearer {img_cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": img_cfg["model"],
                "prompt": prompt,
                "image_size": img_cfg["image_size"],
                "num_inference_steps": 4,
                "batch_size": 1,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        image_url = data["images"][0]["url"]
        img_resp = await client.get(image_url)
        return img_resp.content


def generate_lantern_image_pillow(beautified_text: str, theme: str, config: dict) -> bytes:
    """用 Pillow 程序化合成 Yi Peng 风格天灯图片，返回 PNG bytes。永远不会失败。"""
    from PIL import ImageFilter

    W, H = 512, 512
    img = Image.new("RGBA", (W, H), (2, 3, 8, 255))
    draw = ImageDraw.Draw(img)

    rng = random.Random(hash(beautified_text) & 0xFFFFFFFF)

    # 1. 夜空渐变背景
    for y in range(H):
        t = y / H
        r = int(2 + t * 10)
        g = int(3 + t * 13)
        b = int(8 + t * 20)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # 2. 星星
    for _ in range(80):
        sx = rng.randint(0, W)
        sy = rng.randint(0, int(H * 0.6))
        sb = rng.randint(60, 160)
        ss = rng.choice([1, 1, 1, 2])
        draw.ellipse([sx, sy, sx + ss, sy + ss], fill=(sb, sb, min(255, sb + 30), rng.randint(40, 120)))

    # 3. 背景小天灯光点
    for _ in range(25):
        bx = rng.randint(20, W - 20)
        by = rng.randint(30, int(H * 0.75))
        bs = rng.randint(2, 5)
        ba = rng.randint(30, 100)
        bg_color = (255, rng.randint(160, 210), rng.randint(30, 80), ba)
        glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        gr = bs * 4
        for gi in range(gr, 0, -1):
            ga = max(0, int(ba * 0.3 * gi / gr))
            glow_draw.ellipse([bx - gi, by - gi, bx + gi, by + gi], fill=(255, 180, 50, ga))
        glow_draw.ellipse([bx - bs, by - bs, bx + bs, by + bs], fill=bg_color)
        img = Image.alpha_composite(img, glow_layer)

    # 4. 主天灯 - Yi Peng 柔光椭圆
    cx, cy = W // 2, H // 2 - 20
    ew, eh = 65, 85  # 椭圆半径

    # 外层大气光晕
    for i in range(60, 0, -1):
        alpha = max(0, min(255, int(3.5 * i)))
        expand = i * 3
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse(
            [cx - ew - expand, cy - eh - expand, cx + ew + expand, cy + eh + expand],
            fill=(255, 160, 40, alpha),
        )
        img = Image.alpha_composite(img, glow)

    # 内层暖光晕
    for i in range(30, 0, -1):
        alpha = max(0, min(255, int(6 * i)))
        expand = i * 2
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse(
            [cx - ew - expand, cy - eh - expand, cx + ew + expand, cy + eh + expand],
            fill=(255, 200, 80, alpha),
        )
        img = Image.alpha_composite(img, glow)

    draw = ImageDraw.Draw(img)

    # 灯体椭圆（柔光渐变模拟）
    for i in range(20, 0, -1):
        shrink = (20 - i) * 2
        alpha = min(255, 80 + i * 8)
        r = min(255, 240 + i)
        g = min(255, 190 + i * 3)
        b = min(255, 80 + i * 4)
        draw.ellipse(
            [cx - ew + shrink, cy - eh + shrink, cx + ew - shrink, cy + eh - shrink],
            fill=(r, g, b, alpha),
        )

    # 灯体核心高光
    draw.ellipse(
        [cx - ew + 15, cy - eh + 15, cx + ew - 15, cy + eh - 15],
        fill=(255, 230, 150, 200),
    )
    draw.ellipse(
        [cx - 25, cy - 35, cx + 25, cy + 5],
        fill=(255, 245, 210, 120),
    )

    # 底部火焰
    flame_y = cy + eh - 5
    for fi in range(15, 0, -1):
        fa = min(255, fi * 14)
        draw.ellipse(
            [cx - fi, flame_y - fi // 2, cx + fi, flame_y + fi],
            fill=(255, 200, 60, fa),
        )
    draw.ellipse([cx - 3, flame_y - 2, cx + 3, flame_y + 5], fill=(255, 250, 200, 200))

    # 5. 祝福文字（灯体下方，模仿 display.html 的悬挂标签）
    elegant_path = config["font"].get("elegant", "")
    fallback_path = config["font"]["fallback"]
    try:
        font = ImageFont.truetype(elegant_path, 20)
    except Exception:
        try:
            font = ImageFont.truetype(fallback_path, 20)
        except Exception:
            font = ImageFont.load_default()

    text_y = cy + eh + 35
    # 连接线
    draw.line([(cx, cy + eh + 5), (cx, text_y - 5)], fill=(255, 200, 100, 60), width=1)

    # 文字（最多两行）
    max_w = 280
    words = beautified_text
    lines = []
    cur = ""
    for ch in words:
        test = cur + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = test
    if cur:
        lines.append(cur)
    if len(lines) > 2:
        lines = lines[:2]
        lines[1] = lines[1][:-1] + "…"

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        tx = cx - tw // 2
        ty = text_y + i * 28
        draw.text((tx + 1, ty + 1), line, font=font, fill=(0, 0, 0, 150))
        draw.text((tx, ty), line, font=font, fill=(255, 238, 185, 230))

    # 6. 主题标签
    try:
        small_font = ImageFont.truetype(elegant_path, 14)
    except Exception:
        try:
            small_font = ImageFont.truetype(fallback_path, 14)
        except Exception:
            small_font = ImageFont.load_default()
    theme_label = config["themes"].get(theme, {}).get("emoji", "🏮") + " " + theme
    bbox = draw.textbbox((0, 0), theme_label, font=small_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, H - 40), theme_label, font=small_font, fill=(255, 200, 100, 160))

    # 7. 地面剪影
    points = [(0, H)]
    for x in range(0, W + 8, 8):
        import math
        h = math.sin(x * 0.008) * 8 + math.sin(x * 0.02) * 5 + math.sin(x * 0.05) * 3
        points.append((x, int(H * 0.92 - h)))
    points.append((W, H))
    draw.polygon(points, fill=(5, 3, 2, 240))

    # 地面暖光
    ground_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gg_draw = ImageDraw.Draw(ground_glow)
    for gi in range(80, 0, -1):
        ga = max(0, int(1.5 * gi))
        gg_draw.ellipse(
            [cx - gi * 3, H - gi * 2, cx + gi * 3, H + gi],
            fill=(255, 100, 15, ga),
        )
    img = Image.alpha_composite(img, ground_glow)

    # 输出 PNG
    buf = io.BytesIO()
    final = img.convert("RGB")
    final.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


async def generate_lantern_image(beautified_text: str, theme: str, config: dict) -> tuple[bytes, str]:
    """
    生成天灯图片。优先在线 API，兜底 Pillow。
    返回 (image_bytes, source)。
    """
    api_key = config["image_api"].get("api_key", "")
    if api_key:
        try:
            img_bytes = await generate_lantern_image_api(beautified_text, theme, config)
            return img_bytes, "api"
        except Exception as e:
            logger.warning(f"在线 API 出图失败，回退 Pillow: {e}")

    img_bytes = generate_lantern_image_pillow(beautified_text, theme, config)
    return img_bytes, "pillow"
