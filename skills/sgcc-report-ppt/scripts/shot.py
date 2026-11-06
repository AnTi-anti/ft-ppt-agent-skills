#!/usr/bin/env python3
"""Drop-in replacement for html2png.py using the already-installed Playwright Chromium.

Produces the identical capture contract: viewport 1280x720, deviceScaleFactor = scale,
clip (0,0,1280,720), after document.fonts.ready.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: shot.py <html> <png> [scale]", file=sys.stderr)
        return 2
    html = Path(sys.argv[1]).resolve()
    png = Path(sys.argv[2]).resolve()
    scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    png.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--font-render-hinting=none", "--disable-gpu"])
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=scale)
        page.goto(html.as_uri(), wait_until="networkidle")
        page.evaluate("async () => { await document.fonts.ready; }")
        page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": 1280, "height": 720}, full_page=False)
        browser.close()
    print(f"PNG: {html.name} -> {png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
