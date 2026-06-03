#!/usr/bin/env python3
"""
LAB GROWN DIAMONDの魅力 PP(1).pdf の各ページを高解像度JPGに変換し
pierce-assets/slides/ に配置するスクリプト.

実行:
  python3 scripts/render-pp-slides.py
"""
import os
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
    from PIL import Image
except ImportError:
    print("pip3 install --user pymupdf pillow")
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
os.chdir(REPO)

SRC = Path("/Users/shimamorikento/Downloads/LAB GROWN DIAMONDの魅力　PP(1).pdf")
DST = Path("pierce-assets/slides")
DST.mkdir(parents=True, exist_ok=True)

DPI = 200  # 高解像度
MAX_W = 1600  # 横ピクセル上限 (Webサイズに最適化)

def main():
    print(f"SRC: {SRC}")
    if not SRC.exists():
        print(f"  ! 見つからない")
        sys.exit(1)

    doc = fitz.open(SRC)
    print(f"ページ数: {len(doc)}")
    for i, page in enumerate(doc, 1):
        zoom = DPI / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        tmp = DST / f"_tmp_p{i:02d}.png"
        pix.save(str(tmp))

        # 横ピクセル上限を超えていれば縮小, JPEGで書き出し
        with Image.open(tmp) as img:
            w, h = img.size
            if w > MAX_W:
                ratio = MAX_W / w
                img = img.resize((MAX_W, int(h * ratio)), Image.LANCZOS)
            out = DST / f"slide-{i:02d}.jpg"
            img.convert("RGB").save(out, "JPEG", quality=88, optimize=True)
        tmp.unlink()
        size_kb = out.stat().st_size / 1024
        print(f"  page {i:2d}: {out.name}  {img.size[0]}x{img.size[1]}  {size_kb:.0f} KB")
    doc.close()
    print("=== 完了 ===")


if __name__ == "__main__":
    main()
