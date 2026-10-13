import math
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_liquid_loop():
    renders_dir = r"c:\KIRTSOY_CORE\AI_PROGRAMS\LOGO\renders"
    frames_dir = os.path.join(renders_dir, "temp_frames")
    os.makedirs(frames_dir, exist_ok=True)

    width = 1200
    height = 500
    total_frames = 60

    print(f"Generating {total_frames} frames of liquid metal animation for KIRTSOY...")

    # Load high-tech font
    font = None
    for p in [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\impact.ttf"]:
        if os.path.exists(p):
            try:
                font = ImageFont.truetype(p, 190)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    # Base mask
    base_mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(base_mask)
    text = "KIRTSOY"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (width - tw) // 2
    ty = (height - th) // 2 - 20
    draw.text((tx, ty), text, fill=255, font=font)

    blur_edge = base_mask.filter(ImageFilter.GaussianBlur(radius=6))
    blur_deep = base_mask.filter(ImageFilter.GaussianBlur(radius=18))

    m_px = base_mask.load()
    e_px = blur_edge.load()
    d_px = blur_deep.load()

    # Pre-render frames
    gif_frames = []

    c_base = (235, 245, 255)
    c_dark = (15, 18, 28)
    c_hi = (255, 255, 255)

    for f in range(total_frames):
        t = (f / total_frames) * math.pi * 2 # Seamless circular loop
        frame_img = Image.new("RGBA", (width, height), (7, 8, 11, 255))
        px = frame_img.load()

        for y in range(0, height, 2):
            for x in range(0, width, 2):
                alpha = m_px[x, y]
                if alpha < 15:
                    continue

                be = e_px[x, y] / 255.0
                bd = d_px[x, y] / 255.0

                # Liquid wave simulation
                diag = (x / width) - (y / height)
                wave1 = math.sin(x * 0.015 + y * 0.01 + t * 2.0 + be * 8.0) * 0.5 + 0.5
                wave2 = math.cos(diag * 8.0 - t * 2.0 + bd * 6.0) * 0.5 + 0.5

                specular = math.pow(math.sin(diag * 10.0 + t * 2.0 + be * 6.0) * 0.5 + 0.5, 6.0)
                rim = math.pow(1.0 - (be - bd), 2.5)

                mix_t = max(0.0, min(1.0, wave1 * 0.5 + wave2 * 0.3 + rim * 0.2))

                r = int(c_dark[0] * (1 - mix_t) + c_base[0] * mix_t + c_hi[0] * specular * 0.85)
                g = int(c_dark[1] * (1 - mix_t) + c_base[1] * mix_t + c_hi[1] * specular * 0.85)
                b = int(c_dark[2] * (1 - mix_t) + c_base[2] * mix_t + c_hi[2] * specular * 0.85)

                r = min(255, max(0, r))
                g = min(255, max(0, g))
                b = min(255, max(0, b))

                col = (r, g, b, 255)
                px[x, y] = col
                if x + 1 < width: px[x + 1, y] = col
                if y + 1 < height: px[x, y + 1] = col
                if x + 1 < width and y + 1 < height: px[x + 1, y + 1] = col

        frame_file = os.path.join(frames_dir, f"frame_{f:03d}.png")
        frame_img.save(frame_file)

        # Smaller version for fast lightweight GIF
        gif_frames.append(frame_img.resize((600, 250), Image.Resampling.BILINEAR))

        if (f + 1) % 15 == 0:
            print(f"Rendered {f + 1}/{total_frames} frames...")

    # 1. Save Animated GIF
    gif_path = os.path.join(renders_dir, "kirtsoy-liquid-metal.gif")
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=40,
        loop=0,
        optimize=True
    )
    print(f"Saved Animated GIF: {gif_path}")

    # 2. Compile MP4 with FFmpeg
    mp4_path = os.path.join(renders_dir, "kirtsoy-liquid-metal.mp4")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "30",
        "-i", os.path.join(frames_dir, "frame_%03d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-movflags", "+faststart",
        mp4_path
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Saved High-Res MP4 Video: {mp4_path}")
    except Exception as e:
        print("FFmpeg error:", e)

    # Clean up temp frames
    for f in os.listdir(frames_dir):
        os.remove(os.path.join(frames_dir, f))
    os.rmdir(frames_dir)

    print("ALL ANIMATION DELIVERABLES READY!")

if __name__ == "__main__":
    generate_liquid_loop()
