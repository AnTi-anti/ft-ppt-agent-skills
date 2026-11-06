#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""整册一致性核对：页码序列 / 文件齐全 / 渲染是否落后于 HTML / PPTX 是否同步。

用法:
  python deck_audit.py <run_dir> [deck.pptx]

检查项:
  1. slides/slide-N.html 编号连续（1..N，N 即总页数）
  2. 每页页码 <b>NN / M</b>：NN == 页序，M == 总页数（页面没有页码则跳过）
  3. png/ 与 png-hi/ 每页都有图；png-hi 尺寸必须 3840x2160
  4. png-hi 的修改时间早于 HTML → 提示"忘了重渲染"（WARN）
  5. 传入 deck 时：PPTX 页数 == N，且每页图片与 png-hi 逐页 sha1 一致

退出码: 0 PASS, 2 WARN, 1 FAIL
"""
import hashlib
import os
import re
import sys

from PIL import Image


def main():
    args = [a for a in sys.argv[1:] if a]
    if not args:
        print(__doc__)
        return 2
    run = args[0]
    deck = args[1] if len(args) > 1 else None
    slides = os.path.join(run, "slides")
    png1 = os.path.join(run, "png")
    pnghi = os.path.join(run, "png-hi")

    fails, warns, oks = [], [], []
    if not os.path.isdir(slides):
        print("[FAIL] 找不到 %s" % slides)
        return 1

    files = [f for f in os.listdir(slides) if re.fullmatch(r"slide-\d+\.html", f)]
    nums = sorted(int(re.findall(r"\d+", f)[0]) for f in files)
    total = len(nums)
    if not nums:
        print("[FAIL] slides/ 下没有 slide-N.html")
        return 1
    if nums != list(range(1, total + 1)):
        fails.append("HTML 编号不连续: %s" % nums[:15])
    else:
        oks.append("HTML 共 %d 页，编号连续" % total)

    counter_bad = []
    stale = []
    missing = []
    for n in range(1, total + 1):
        html = os.path.join(slides, "slide-%d.html" % n)
        s = open(html, encoding="utf-8").read()
        m = re.search(r"<b>\s*(\d{1,3})\s*/\s*(\d{1,3})\s*</b>", s)
        if m:
            if int(m.group(1)) != n:
                counter_bad.append("第 %d 页页码写成 %s" % (n, m.group(0)))
            elif int(m.group(2)) != total:
                counter_bad.append("第 %d 页总页数写成 %d（应为 %d）" % (n, int(m.group(2)), total))
        for d, tag in ((png1, "png"), (pnghi, "png-hi")):
            f = os.path.join(d, "slide-%d.png" % n)
            if not os.path.exists(f):
                missing.append("%s/slide-%d.png" % (tag, n))
        fh = os.path.join(pnghi, "slide-%d.png" % n)
        if os.path.exists(fh) and os.path.getmtime(fh) < os.path.getmtime(html) - 1:
            stale.append(n)

    if counter_bad:
        fails.extend(counter_bad[:8])
    else:
        oks.append("页码计数与页序一致")
    if missing:
        fails.append("缺图: %s" % ", ".join(missing[:8]))
    else:
        oks.append("png / png-hi 文件齐全")
    if stale:
        warns.append("第 %s 页 3x 渲染早于 HTML，可能忘了重渲染" % ",".join(map(str, stale[:10])))

    size_bad = []
    for n in range(1, total + 1):
        f = os.path.join(pnghi, "slide-%d.png" % n)
        if os.path.exists(f):
            w, h = Image.open(f).size
            if (w, h) != (3840, 2160):
                size_bad.append((n, w, h))
    if size_bad:
        fails.append("3x 尺寸异常: %s" % size_bad[:5])
    else:
        oks.append("3x 图均为 3840x2160")

    if deck:
        if not os.path.exists(deck):
            fails.append("找不到 PPTX: %s" % deck)
        else:
            from pptx import Presentation
            prs = Presentation(deck)
            if len(prs.slides) != total:
                fails.append("PPTX 页数 %d ≠ HTML %d 页" % (len(prs.slides), total))
            else:
                mism = []
                for i, slide in enumerate(prs.slides, 1):
                    pics = [sh for sh in slide.shapes if sh.shape_type == 13]
                    if len(pics) != 1:
                        mism.append((i, "picture 数=%d" % len(pics)))
                        continue
                    want = hashlib.sha1(open(os.path.join(pnghi, "slide-%d.png" % i), "rb").read()).hexdigest()
                    if hashlib.sha1(pics[0].image.blob).hexdigest() != want:
                        mism.append((i, "图片与 png-hi 不一致"))
                if mism:
                    fails.append("PPTX 未同步: %s" % mism[:6])
                else:
                    oks.append("PPTX %d 页与 3x 图逐页一致" % total)

    status = "FAIL" if fails else ("WARN" if warns else "PASS")
    print("status:", status)
    for m in oks:
        print("  +", m)
    if warns:
        print("[WARN] %d" % len(warns))
        for m in warns:
            print("  !", m)
    if fails:
        print("[FAIL] %d" % len(fails))
        for m in fails:
            print("  x", m)
    print("\n页数：%d" % total)
    return 1 if fails else (2 if warns else 0)


if __name__ == "__main__":
    sys.exit(main())
