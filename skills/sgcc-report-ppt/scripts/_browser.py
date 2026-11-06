#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""选择可用浏览器，供 shot.py / visual_qa.py 共用。

顺序：
  1. SHOT_CHANNEL 环境变量（"chromium" / "msedge" / "chrome"）
  2. Playwright 自带 Chromium
  3. 系统 Microsoft Edge（Windows 自带，内网无需下载浏览器）
  4. 系统 Google Chrome

内网/离线环境只要装了 Edge 就能渲染，无需 `playwright install chromium`。
"""
import os
import sys

ARGS = ["--font-render-hinting=none", "--disable-gpu"]


def open_browser(p, quiet=False):
    forced = (os.environ.get("SHOT_CHANNEL") or "").strip()
    order = [forced] if forced else [None, "msedge", "chrome"]
    last = None
    for ch in order:
        kw = {"args": ARGS}
        if ch and ch != "chromium":
            kw["channel"] = ch
        try:
            b = p.chromium.launch(**kw)
            if ch and ch != "chromium" and not quiet:
                print("[info] 使用系统浏览器 channel=%s" % ch, file=sys.stderr)
            return b
        except Exception as e:  # noqa: BLE001 - 逐个回退
            last = e
    raise last
