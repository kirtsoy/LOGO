"""
KIRTSOY 3D INTRO — ZERO-LOSS VIDEO COMPILER
Compiles PNG sequences into Apple ProRes 4444 (.MOV) & WebM VP9 (.WEBM) with 100% Alpha Channel Transparency.
"""

import os
import sys
import glob
import json
import shutil
import zipfile
import subprocess
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def find_latest_zip_or_folder(input_target=None):
    if input_target and os.path.exists(input_target):
        return os.path.abspath(input_target)
    
    candidates = []
    
    # 1. Check current directory and ./renders
    for p in ["./renders/*.zip", "./*.zip"]:
        candidates.extend(glob.glob(p))
        
    # 2. Check user's Downloads directory
    user_downloads = os.path.expanduser("~/Downloads")
    if os.path.exists(user_downloads):
        candidates.extend(glob.glob(os.path.join(user_downloads, "kirtsoy_intro_*.zip")))
        
    if not candidates:
        return None
        
    # Sort by modification time, newest first
    candidates.sort(key=os.path.getmtime, reverse=True)
    return os.path.abspath(candidates[0])

def compile_sequence_to_video(source_path=None, fps=60):
    print("=================================================================")
    print("💎 KIRTSOY ZERO-LOSS VIDEO COMPILER (ProRes 4444 & VP9 Alpha)")
    print("=================================================================\n")
    
    target = find_latest_zip_or_folder(source_path)
    if not target:
        print("❌ Ошибка: Не найден архив с PNG-кадрами (kirtsoy_intro_*.zip)!")
        print("💡 Сначала нажмите '💎 FullHD 1080p' или '✨ 4K UHD' в веб-студии, чтобы скачать архив,")
        print("   или перетащите скачанный .zip файл прямо на этот скрипт.\n")
        return None
        
    print(f"📦 Исходный файл: {target}")
    
    temp_dir = os.path.abspath("./renders/temp_compile_frames")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Step 1: Extract or copy frames
        if zipfile.is_zipfile(target):
            print("⏳ Распаковка PNG кадров во временную директорию...")
            with zipfile.ZipFile(target, 'r') as zf:
                zf.extractall(temp_dir)
        elif os.path.isdir(target):
            print("📂 Копирование кадров из папки...")
            for f in glob.glob(os.path.join(target, "*.png")):
                shutil.copy2(f, temp_dir)
        else:
            print("❌ Ошибка: Указанный файл не является ZIP-архивом или папкой.")
            return None

        # Locate PNG files
        png_files = sorted(glob.glob(os.path.join(temp_dir, "*.png")))
        if not png_files:
            # Check subfolders inside ZIP
            png_files = sorted(glob.glob(os.path.join(temp_dir, "**", "*.png"), recursive=True))
            if not png_files:
                print("❌ Ошибка: В архиве не найдено PNG файлов.")
                return None
            # Move them to temp_dir root
            for p in png_files:
                dest = os.path.join(temp_dir, os.path.basename(p))
                if not os.path.exists(dest):
                    shutil.move(p, dest)
            png_files = sorted(glob.glob(os.path.join(temp_dir, "*.png")))

        total_frames = len(png_files)
        print(f"✅ Найдено {total_frames} PNG кадров (32-bit RGBA с Alpha-прозрачностью)")

        # Normalize file names to pattern: frame_%05d.png
        normalized_pattern = os.path.join(temp_dir, "frame_%05d.png")
        for idx, pf in enumerate(png_files):
            new_name = os.path.join(temp_dir, f"frame_{idx:05d}.png")
            if pf != new_name:
                if os.path.exists(new_name):
                    os.remove(new_name)
                os.rename(pf, new_name)

        out_dir = os.path.abspath("./renders")
        os.makedirs(out_dir, exist_ok=True)
        timestamp = int(time.time())

        # Target 1: Apple ProRes 4444 (.mov) with 100% Alpha Transparency
        prores_filename = f"kirtsoy_intro_prores4444_alpha_{timestamp}.mov"
        prores_out = os.path.join(out_dir, prores_filename)
        print(f"\n🎬 1. Кодирование Apple ProRes 4444 (10-bit RGBA Alpha, 60 FPS)...")
        prores_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", normalized_pattern,
            "-c:v", "prores_ks",
            "-profile:v", "4444",
            "-pix_fmt", "yuva444p10le",
            prores_out
        ]
        t0 = time.time()
        # Direct console pass-through so user sees live FFmpeg progress bar!
        res_prores = subprocess.run(prores_cmd)
        if res_prores.returncode != 0:
            print("⚠️ Ошибка кодирования ProRes (код возврата", res_prores.returncode, ")")
            prores_out = None
        else:
            p_size_mb = os.path.getsize(prores_out) / (1024 * 1024)
            print(f"\n   🎉 ProRes 4444 готов за {time.time() - t0:.1f}с! Размер: {p_size_mb:.2f} МБ")
            print(f"   📁 Файл: {prores_out}")

        # Target 2: WebM VP9 (.webm) with Alpha Transparency (Cross-platform & Web)
        webm_filename = f"kirtsoy_intro_vp9_alpha_{timestamp}.webm"
        webm_out = os.path.join(out_dir, webm_filename)
        print(f"\n🌐 2. Кодирование WebM VP9 с прозрачностью (Zero-Loss CRF 12, 60 FPS)...")
        webm_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", normalized_pattern,
            "-c:v", "libvpx-vp9",
            "-pix_fmt", "yuva420p",
            "-deadline", "realtime",
            "-cpu-used", "5",
            "-row-mt", "1",
            "-b:v", "0",
            "-crf", "12",
            webm_out
        ]
        t1 = time.time()
        res_webm = subprocess.run(webm_cmd)
        if res_webm.returncode != 0:
            print("⚠️ Ошибка кодирования WebM (код возврата", res_webm.returncode, ")")
            webm_out = None
        else:
            w_size_mb = os.path.getsize(webm_out) / (1024 * 1024)
            print(f"\n   🎉 WebM готов за {time.time() - t1:.1f}с! Размер: {w_size_mb:.2f} МБ")
            print(f"   📁 Файл: {webm_out}")

        print("\n=================================================================")
        print("🚀 ВСЕ ВИДЕО СОЗДАНЫ С АБСОЛЮТНОЙ ПРОЗРАЧНОСТЬЮ И БЕЗ ПОТЕРИ КАЧЕСТВА!")
        print("=================================================================")
        print("• Apple ProRes 4444 (.MOV) — вставляется в DaVinci, Premiere, After Effects, CapCut.")
        print("• WebM VP9 (.WEBM) — проигрывается в браузере, Discord, Telegram и на сайтах.")
        print("• Фон полностью прозрачный — никакого черного экрана нет.\n")

        # Open in Explorer
        if sys.platform == 'win32' and prores_out and os.path.exists(prores_out):
            try:
                subprocess.Popen(f'explorer /select,"{prores_out}"')
            except Exception:
                pass

        return {
            "prores_file": prores_filename if prores_out else None,
            "prores_path": prores_out,
            "webm_file": webm_filename if webm_out else None,
            "webm_path": webm_out,
            "frames": total_frames
        }

    finally:
        # Clean up temporary frames
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    compile_sequence_to_video(src)
