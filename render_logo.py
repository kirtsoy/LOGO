import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

def create_liquid_metal_logo():
    output_dir = r"c:\KIRTSOY_CORE\AI_PROGRAMS\LOGO\renders"
    os.makedirs(output_dir, exist_ok=True)

    width = 2400
    height = 900
    scale = 2
    w_high = width * scale
    h_high = height * scale

    # 1. Base High-Res Text Mask
    mask = Image.new("L", (w_high, h_high), 0)
    draw = ImageDraw.Draw(mask)

    # Try to load high-tech font if available, or draw crisp stylized glyphs
    font = None
    font_paths = [
        r"C:\Windows\Fonts\orbitron-black.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\impact.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                font = ImageFont.truetype(p, 420)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    text = "KIRTSOY"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (w_high - text_w) // 2
    y = (h_high - text_h) // 2 - 40

    draw.text((x, y), text, fill=255, font=font)

    # 2. Beveled Distance & Normal Map
    blur1 = mask.filter(ImageFilter.GaussianBlur(radius=8))
    blur2 = mask.filter(ImageFilter.GaussianBlur(radius=24))
    blur3 = mask.filter(ImageFilter.GaussianBlur(radius=48))

    # Chrome Themes to Render
    themes = [
        {
            "name": "kirtsoy-platinum-chrome.png",
            "base_color": (230, 240, 255),
            "dark_color": (20, 24, 38),
            "highlight": (255, 255, 255),
            "accent": (140, 180, 255)
        },
        {
            "name": "kirtsoy-molten-24k-gold.png",
            "base_color": (255, 215, 80),
            "dark_color": (45, 25, 5),
            "highlight": (255, 250, 220),
            "accent": (255, 170, 30)
        },
        {
            "name": "kirtsoy-cyberpunk-neon.png",
            "base_color": (120, 230, 255),
            "dark_color": (30, 10, 45),
            "highlight": (255, 100, 220),
            "accent": (90, 120, 255)
        },
        {
            "name": "kirtsoy-obsidian-stealth.png",
            "base_color": (110, 120, 135),
            "dark_color": (8, 10, 14),
            "highlight": (220, 230, 245),
            "accent": (70, 80, 95)
        }
    ]

    for theme in themes:
        img = Image.new("RGBA", (w_high, h_high), (0, 0, 0, 0))
        pixels = img.load()
        m_pixels = mask.load()
        b1_pixels = blur1.load()
        b2_pixels = blur2.load()
        b3_pixels = blur3.load()

        c_base = theme["base_color"]
        c_dark = theme["dark_color"]
        c_hi = theme["highlight"]
        c_acc = theme["accent"]

        step = 2
        for py in range(0, h_high, step):
            for px in range(0, w_high, step):
                alpha = m_pixels[px, py]
                if alpha < 10:
                    continue

                b1 = b1_pixels[px, py] / 255.0
                b2 = b2_pixels[px, py] / 255.0
                b3 = b3_pixels[px, py] / 255.0

                # Simulated Liquid Metal Curvature & Reflection Waves
                diag = (px / w_high) - (py / h_high)
                wave = math.sin(px * 0.008 + py * 0.005 + b1 * 12.0) * 0.5 + 0.5
                fresnel = math.pow(1.0 - (b1 - b2), 2.0)
                specular = math.pow(math.sin(diag * 6.0 + b1 * 8.0) * 0.5 + 0.5, 8.0)

                # Metallic mix
                t = (wave * 0.5 + b2 * 0.3 + fresnel * 0.2)
                t = max(0.0, min(1.0, t))

                r = int(c_dark[0] * (1 - t) + c_base[0] * t + c_hi[0] * specular * 0.8)
                g = int(c_dark[1] * (1 - t) + c_base[1] * t + c_hi[1] * specular * 0.8)
                b = int(c_dark[2] * (1 - t) + c_base[2] * t + c_hi[2] * specular * 0.8)

                r = min(255, max(0, r))
                g = min(255, max(0, g))
                b = min(255, max(0, b))

                col = (r, g, b, alpha)
                pixels[px, py] = col
                if px + 1 < w_high: pixels[px + 1, py] = col
                if py + 1 < h_high: pixels[px, py + 1] = col
                if px + 1 < w_high and py + 1 < h_high: pixels[px + 1, py + 1] = col

        # Downsample for crisp supersampled antialiasing
        final_img = img.resize((width, height), Image.Resampling.LANCZOS)
        out_path = os.path.join(output_dir, theme["name"])
        final_img.save(out_path, "PNG")
        print(f"Rendered: {out_path}")

    print("All renders completed successfully!")

if __name__ == "__main__":
    create_liquid_metal_logo()
