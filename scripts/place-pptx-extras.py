#!/usr/bin/env python3
"""
.pptx 抽出画像のうち未使用 8 枚を pierce-assets/hi-res/ に配置.
"""
import os
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("pip3 install --user pillow")
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
os.chdir(REPO)

SRC = Path("pptx-extract")
DST = Path("pierce-assets/hi-res")
DST.mkdir(parents=True, exist_ok=True)

# 17 枚の残り (用途別 descriptive name)
MAPPING = [
    # 既存9枚は scripts/place-pptx-hires.py で配置済
    ("image1.jpeg", "wood-floor-thin.jpg",       "copy"),
    ("image2.jpg",  "frames-on-wall.jpg",        "copy"),    # 3枚額のモックアップ
    ("image7.jpg",  "diamond-on-leaves.jpg",     "copy"),    # サステナブル: 葉とダイヤ
    ("image8.jpeg", "wood-floor-thick.jpg",      "copy"),
    ("image9.jpg",  "diamond-macro.jpg",         "copy"),    # 単石マクロ
    ("image14.png", "diamond-tiny.jpg",          "png2jpg"), # 小粒シンボル
    ("image15.png", "chart-clarity-thumb.jpg",   "png2jpg"), # サムネ版クラリティ
    ("image16.png", "chart-cut-with-side.jpg",   "png2jpg"), # 横顔付カット
]

MAX_W = 2400

def process(src: Path, dst: Path, mode: str):
    if mode == "copy":
        with Image.open(src) as img:
            w, h = img.size
        if w > MAX_W:
            with Image.open(src) as img:
                ratio = MAX_W / w
                img = img.resize((MAX_W, int(h * ratio)), Image.LANCZOS)
                img.convert("RGB").save(dst, "JPEG", quality=92, optimize=True)
            print(f"  {src.name} → {dst.name} (resized {w}x{h} → {MAX_W}x{int(h*ratio)})")
        else:
            shutil.copy(src, dst)
            print(f"  {src.name} → {dst.name} (copied {w}x{h})")
        return
    if mode == "png2jpg":
        with Image.open(src) as img:
            w, h = img.size
            if w > MAX_W:
                ratio = MAX_W / w
                img = img.resize((MAX_W, int(h * ratio)), Image.LANCZOS)
                w, h = img.size
            img.convert("RGB").save(dst, "JPEG", quality=92, optimize=True)
        before = src.stat().st_size; after = dst.stat().st_size
        print(f"  {src.name} → {dst.name} ({w}x{h}, {before/1024:.0f}KB→{after/1024:.0f}KB)")


for s, d, m in MAPPING:
    src = SRC / s
    dst = DST / d
    if not src.exists():
        print(f"  ! 見つからない: {src}")
        continue
    process(src, dst, m)
print("=== 完了 ===")
