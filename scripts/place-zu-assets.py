#!/usr/bin/env python3
"""
ユーザーが手動で配置した「図1〜図16」をpierce-assets/zu/ に英数字名でコピー.
これらはスライドの内容を反映するための公式素材.
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

DST = Path("pierce-assets/zu")
DST.mkdir(parents=True, exist_ok=True)

# (図番号, 配置先英数字名, 元拡張子)
# スライドの内容との対応:
MAPPING = [
    (1,  "01-lab-vs-natural",   ".png"),   # Slide1 Lab×Natural 比較
    (2,  "02-pair-diamonds",    ".png"),   # Slide1 ペアダイヤ
    (3,  "03-igi-report",       ".jpg"),   # Slide2 POINT1 IGI証明書
    (4,  "04-top-side-large",   ".jpg"),   # Slide3 POINT2 上面+側面
    (5,  "05-on-leaves",        ".jpg"),   # Slide4 POINT3 葉の上
    (6,  "06-top-side-small",   ".jpg"),   # Slide3 派生 上面+側面 小
    (7,  "07-grade-overview",   ".png"),   # Slide5 取扱グレード一覧 (図7-10同一)
    (11, "11-natural-i3",       ".jpg"),   # Slide6 自然側
    (12, "12-lab-vs1-ex",       ".png"),   # Slide6 ラボグロウン側
    (13, "13-chart-color",      ".jpg"),   # Slide7 カラーチャート
    (14, "14-chart-clarity",    ".png"),   # Slide8 クラリティチャート
    (15, "15-chart-cut",        ".png"),   # Slide9 カットチャート
    (16, "16-chart-size",       ".jpg"),   # Slide10 サイズチャート
]
# 図8,9,10は図7と同一なのでスキップ

MAX_W = 2400

def process(num: int, name: str, ext: str):
    src_candidates = [
        Path(f"図{num}.png"),
        Path(f"図{num}.jpg"),
        Path(f"図{num}.jpeg"),
    ]
    src = next((c for c in src_candidates if c.exists()), None)
    if not src:
        print(f"  ! 図{num} 見つからない")
        return
    dst = DST / f"{name}{ext}"
    with Image.open(src) as img:
        w, h = img.size
        if w > MAX_W:
            ratio = MAX_W / w
            img = img.resize((MAX_W, int(h * ratio)), Image.LANCZOS)
            w, h = img.size
        if ext == ".jpg":
            img.convert("RGB").save(dst, "JPEG", quality=92, optimize=True)
        else:
            img.save(dst, optimize=True)
    print(f"  図{num} → zu/{dst.name}  {w}x{h}  {dst.stat().st_size/1024:.0f}KB")

for n, name, ext in MAPPING:
    process(n, name, ext)
print("=== 完了 ===")
