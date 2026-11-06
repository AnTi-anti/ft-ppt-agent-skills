#!/usr/bin/env python3
"""把 HTML 页面渲染成 PNG（Playwright）。

渲染契约：视口 1280×720，deviceScaleFactor = scale，截图区域固定 1280×720，
等待 document.fonts.ready 之后再截。

浏览器选择顺序：
  1. SHOT_CHANNEL 环境变量指定（"chromium" / "msedge" / "chrome"）
  2. Playwright 自带 Chromium
  3. 系统已安装的 Microsoft Edge（Windows 自带，内网离线环境无需下载浏览器）
  4. 系统已安装的 Google Chrome
"""
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ARGS = ["--font-render-hinting=none", "--disable-gpu"]


def open_browser(p):
    forced = (os.environ.get("SHOT_CHANNEL") or "").strip()
    order = [forced] if forced else [None, "msedge", "chrome"]
    last = None
    for ch in order:
        kw = {"args": ARGS}
        if ch and ch != "chromium":
            kw["channel"] = ch
        try:
            b = p.chromium.launch(**kw)
            if ch and ch != "chromium":
                print("[info] 使用系统浏览器 channel=%s" % ch, file=sys.stderr)
            return b
        except Exception as e:  # noqa: BLE001 - 逐个回退
            last = e
    raise last


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: shot.py <html> <png> [scale]", file=sys.stderr)
        return 2
    html = Path(sys.argv[1]).resolve()
    png = Path(sys.argv[2]).resolve()
    scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    png.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = open_browser(p)
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=scale)
        page.goto(html.as_uri(), wait_until="networkidle")
        page.evaluate("async () => { await document.fonts.ready; }")
        page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": 1280, "height": 720}, full_page=False)
        browser.close()
    print(f"PNG: {html.name} -> {png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
