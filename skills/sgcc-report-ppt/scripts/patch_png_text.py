#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""在图片上替换一行文字（用于文字已烘焙进图片、又没有源脚本可改的场景）。

用法:
  # 1) 先定位：打印区域内暗色文字的整行区间（y 起止 + x 范围）
  python patch_png_text.py fig.png --probe --box x1,y1,x2,y2

  # 2) 再替换：用背景色盖掉整行，按同字体/字号居中重绘
  python patch_png_text.py fig.png --box x1,y1,x2,y2 --text "月电量预测76%" \
      [--font C:/Windows/Fonts/msyh.ttc] [--size 26] [--color 0,0,0] [--bg auto]

说明:
  - --box 建议略大于文字：左右各留 5–10px、上下各留 3–5px
  - --bg auto 时取 box 四角像素的众数作为背景色（要求背景均匀）
  - 默认自动备份为 <png>.bak.png（已存在则不覆盖），方便回退
  - 改完请重新渲染该页并组包，再用 deck_audit.py 复核
"""
import os
import shutil
import sys
from collections import Counter

from PIL import Image, ImageDraw, ImageFont


def parse_box(s):
    parts = [int(float(v)) for v in s.split(",")]
    if len(parts) != 4:
        raise ValueError("--box 需要 x1,y1,x2,y2")
    return parts


def dark_bands(im, box, thr=330):
    x1, y1, x2, y2 = box
    crop = im.crop((x1, y1, x2, y2)).convert("RGB")
    w, h = crop.size
    px = crop.load()
    rows = []
    for y in range(h):
        hit = False
        for x in range(0, w):
            r, g, b = px[x, y]
            if r + g + b < thr:
                hit = True
                break
        rows.append(hit)
    bands, start = [], None
    for y, v in enumerate(rows):
        if v and start is None:
            start = y
        if not v and start is not None:
            bands.append((y1 + start, y1 + y - 1))
            start = None
    if start is not None:
        bands.append((y1 + start, y1 + h - 1))
    out = []
    for a, b in bands:
        xs = []
        for y in range(a - y1, b - y1 + 1):
            for x in range(w):
                r, g, bb = px[x, y]
                if r + g + bb < thr:
                    xs.append(x)
        out.append((a, b, x1 + min(xs), x1 + max(xs)) if xs else (a, b, None, None))
    return out


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    png = args[0]
    opts = {}
    i = 1
    while i < len(args):
        a = args[i]
        if a.startswith("--"):
            key = a[2:]
            if key in ("probe", "backup"):
                opts[key] = True
            else:
                opts[key] = args[i + 1]
                i += 1
        i += 1

    im = Image.open(png).convert("RGB")
    box = parse_box(opts["box"])

    if opts.get("probe"):
        for a, b, xa, xb in dark_bands(im, box):
            print("行带 y=%d..%d  x=%s..%s  (高 %d)" % (a, b, xa, xb, b - a + 1))
        return 0

    text = opts.get("text")
    if not text:
        print("缺少 --text")
        return 2
    font_path = opts.get("font", "C:/Windows/Fonts/msyh.ttc")
    size = int(opts.get("size", 26))
    color = tuple(int(v) for v in opts.get("color", "0,0,0").split(","))
    bg = opts.get("bg", "auto")
    if bg == "auto":
        x1, y1, x2, y2 = box
        corners = [im.getpixel((x1, y1)), im.getpixel((x2 - 1, y1)),
                   im.getpixel((x1, y2 - 1)), im.getpixel((x2 - 1, y2 - 1))]
        bg = Counter(corners).most_common(1)[0][0]
        print("背景色(auto):", bg)
    else:
        bg = tuple(int(v) for v in bg.split(","))

    bak = png + ".bak.png"
    if not os.path.exists(bak):
        shutil.copy2(png, bak)
        print("备份:", os.path.basename(bak))

    d = ImageDraw.Draw(im)
    d.rectangle(box, fill=bg)
    font = ImageFont.truetype(font_path, size)
    cx = (box[0] + box[2]) // 2
    cy = (box[1] + box[3]) // 2
    d.text((cx, cy), text, font=font, fill=color, anchor="mm")
    im.save(png)
    bb = d.textbbox((cx, cy), text, font=font, anchor="mm")
    print("已替换 -> %s" % text)
    print("文字 bbox: x %d..%d, y %d..%d（box: %s）" % (bb[0], bb[2], bb[1], bb[3], box))
    if bb[0] < box[0] or bb[2] > box[2] or bb[1] < box[1] or bb[3] > box[3]:
        print("⚠ 文字超出 box，请调大 --box 或减小 --size 后重做（可从 .bak.png 恢复）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
