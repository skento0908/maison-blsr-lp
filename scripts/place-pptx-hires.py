#!/usr/bin/env python3
"""
.pptx から抽出した原寸画像を pierce-assets/hi-res/ に最適化配置するスクリプト.

ポリシー:
  - 原寸の解像度はそのまま (再サンプリングしない / 横 2400px 超のみ縮小)
  - PNG はサイズ大きいので q=92 で JPEG に変換
  - 元から JPEG のものは無変換コピー (再圧縮で画質を落とさない)

実行:
  python3 scripts/place-pptx-hires.py
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

# (元ファイル, 配置先ファイル名, 動作)
# 動作: "copy" = 無変換コピー, "png2jpg" = PNG→JPEG変換
MAPPING = [
    ("image4.png",  "lab-grown-pair-hero.jpg",      "png2jpg"),
    ("image3.png",  "lab-vs-natural-square.jpg",    "png2jpg"),
    ("image5.jpg",  "diamond-igi-report.jpg",       "copy"),
    ("image6.jpg",  "diamond-top-side.jpg",         "copy"),
    ("image13.jpg", "natural-with-inclusions.jpg",  "copy"),
    ("image11.jpg", "chart-color.jpg",              "copy"),
    ("image12.jpg", "chart-clarity.jpg",            "copy"),
    ("image10.jpg", "chart-cut.jpg",                "copy"),
    ("image17.jpg", "chart-size.jpg",               "copy"),
]

MAX_W = 2400  # これ以上は LANCZOS で縮小


def process(src: Path, dst: Path, mode: str):
    if mode == "copy":
        with Image.open(src) as img:
            w, h = img.size
        if w > MAX_W:
            with Image.open(src) as img:
                ratio = MAX_W / w
                resized = img.resize((MAX_W, int(h * ratio)), Image.LANCZOS)
                resized.convert("RGB").save(dst, "JPEG", quality=92, optimize=True)
            print(f"  {src.name} → {dst.name}  (resized {w}x{h} → {MAX_W}x{int(h*ratio)})")
        else:
            shutil.copy(src, dst)
            print(f"  {src.name} → {dst.name}  (copied {w}x{h})")
        return

    if mode == "png2jpg":
        with Image.open(src) as img:
            w, h = img.size
            if w > MAX_W:
                ratio = MAX_W / w
                img = img.resize((MAX_W, int(h * ratio)), Image.LANCZOS)
                w, h = img.size
            img.convert("RGB").save(dst, "JPEG", quality=92, optimize=True)
        before = src.stat().st_size
        after = dst.stat().st_size
        print(f"  {src.name} → {dst.name}  ({w}x{h}, {before/1024:.0f}KB → {after/1024:.0f}KB)")


def main():
    print(f"REPO: {REPO}")
    print(f"配置先: {DST}")
    print()
    for src_name, dst_name, mode in MAPPING:
        src = SRC / src_name
        dst = DST / dst_name
        if not src.exists():
            print(f"  ! 見つからない: {src}")
            continue
        process(src, dst, mode)
    print()
    print("=== 配置完了 ===")
    for f in sorted(DST.iterdir()):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name}: {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
