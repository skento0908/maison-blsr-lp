#!/usr/bin/env python3
"""
press.html から press.pdf を生成するスクリプト。

前提:
  pip3 install --user playwright pillow pymupdf
  python3 -m playwright install chromium

実行 (リポジトリのルートから):
  python3 scripts/generate-press-pdf.py
"""
import os
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
    from playwright.sync_api import sync_playwright
except ImportError:
    print("依存関係をインストールしてください:")
    print("  pip3 install --user playwright pillow pymupdf")
    print("  python3 -m playwright install chromium")
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
os.chdir(REPO)

SRC = Path("press-images")
PRINT = Path("press-images-print")
HTML = Path("press.html")
TMP_HTML = Path("_press_print.html")
OUT = Path("press.pdf")


def resize_save(src: Path, dst: Path, max_size: tuple[int, int], quality: int = 82):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        img = img.convert("RGB")
        img.thumbnail(max_size, Image.LANCZOS)
        img.save(dst, "JPEG", quality=quality, optimize=True)


def build_print_images():
    """PDF表示サイズに合わせて画像を縮小コピー."""
    if PRINT.exists():
        shutil.rmtree(PRINT)
    configs = [
        ("celebrity", (600, 600), 82),
        ("tv",        (300, 200), 80),
        ("magazines", (1000, 600), 80),
    ]
    for sub, max_size, quality in configs:
        src_dir = SRC / sub
        dst_dir = PRINT / sub
        for f in sorted(src_dir.iterdir()):
            if f.suffix.lower() in (".jpg", ".jpeg"):
                resize_save(f, dst_dir / f.name, max_size, quality)
        print(f"  optimized: {sub}/")


def build_print_html():
    """press.html を読み込んで画像パスを print 用に差し替えた一時HTMLを書き出す."""
    html = HTML.read_text(encoding="utf-8")
    modified = html.replace("press-images/", "press-images-print/")
    # PDFダウンロードのhrefは元に戻す
    modified = modified.replace('href="press-images-print/', 'href="press-images/')
    TMP_HTML.write_text(modified, encoding="utf-8")


def render_pdf():
    """Chromium ヘッドレスでPDFを書き出す."""
    html_url = "file://" + str(TMP_HTML.resolve())
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(html_url, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(2500)  # フォント+画像読み込み
        page.pdf(
            path=str(OUT),
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
            prefer_css_page_size=True,
        )
        browser.close()


def cleanup():
    if TMP_HTML.exists():
        TMP_HTML.unlink()


def main():
    print(f"REPO: {REPO}")
    print("Step 1/3: 画像を縮小...")
    build_print_images()
    print("Step 2/3: 一時HTMLを構成...")
    build_print_html()
    print("Step 3/3: PDFをレンダリング...")
    render_pdf()
    cleanup()

    size_kb = OUT.stat().st_size / 1024
    print()
    print(f"✓ Generated: {OUT}")
    print(f"  Size: {size_kb:.1f} KB ({size_kb/1024:.2f} MB)")
    print()
    print("press-images-print/ は再生成可能なので .gitignore で除外しています。")


if __name__ == "__main__":
    main()
