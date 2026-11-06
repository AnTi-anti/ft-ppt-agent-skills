#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从整套产物中删除一页：PPTX 删页 + 文件重命名 + 页码重排（章节号需手工改）。

用法:
  python delete_slide.py <deck.pptx> <page_no> [--dry-run]

它会做四件事（全部可重复核）：
  1. 备份 deck 为 <deck>.pre-delete.pptx（同名已存在则不覆盖）
  2. 从 PPTX 中移除第 page_no 页（sldIdLst）
  3. 删除 slides/slide-K.html、png/slide-K.png、png-hi/slide-K.png，
     并把 K+1..N 的文件整体前移一位（N→N-1）
  4. 把所有 <b>NN / M</b> 页码改成新页序与新的总页数

不做的事：章节号（如 2.1.4→2.1.3）、目录、正文交叉引用——这些是内容，改完请重渲染。

完成后按提示执行：
  for n in 1..N-1: shot.py 1x + 3x
  replace_all_slides_pptx.py <deck> png-hi
"""
import os
import re
import shutil
import sys


def main():
    args = [a for a in sys.argv[1:] if a]
    dry = "--dry-run" in args
    args = [a for a in args if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        return 2
    deck = os.path.abspath(args[0])
    k = int(args[1])
    run = os.path.dirname(deck)

    from pptx import Presentation
    prs = Presentation(deck)
    total = len(prs.slides)
    if not (1 <= k <= total):
        print("page_no 超出范围：1..%d" % total)
        return 2

    slides = os.path.join(run, "slides")
    plan = []
    for n in range(k + 1, total + 1):
        plan.append((os.path.join(slides, "slide-%d.html" % n), os.path.join(slides, "slide-%d.html" % (n - 1))))
        for d in ("png", "png-hi"):
            plan.append((os.path.join(run, d, "slide-%d.png" % n), os.path.join(run, d, "slide-%d.png" % (n - 1))))

    print("将从 %d 页的 deck 删除第 %d 页，剩余 %d 页" % (total, k, total - 1))
    for src, dst in plan[:6]:
        print("  rename", os.path.relpath(src, run), "->", os.path.relpath(dst, run))
    if len(plan) > 6:
        print("  ... 共 %d 个文件" % len(plan))
    if dry:
        print("[dry-run] 未做任何修改")
        return 0

    bak = deck.replace(".pptx", ".pre-delete.pptx")
    if not os.path.exists(bak):
        shutil.copy2(deck, bak)
        print("备份:", os.path.basename(bak))

    # 1) PPTX 删页
    lst = prs.slides._sldIdLst
    items = list(lst)
    lst.remove(items[k - 1])
    prs.save(deck)
    print("PPTX 已删页，剩余", len(Presentation(deck).slides), "页")

    # 2) 文件删除 + 前移
    for f in (os.path.join(slides, "slide-%d.html" % k),
              os.path.join(run, "png", "slide-%d.png" % k),
              os.path.join(run, "png-hi", "slide-%d.png" % k)):
        if os.path.exists(f):
            os.remove(f)
    for src, dst in plan:
        if os.path.exists(src):
            if os.path.exists(dst):
                os.remove(dst)
            os.replace(src, dst)
    print("文件已重命名")

    # 3) 页码重排
    new_total = total - 1
    cnt = 0
    for n in range(1, new_total + 1):
        p = os.path.join(slides, "slide-%d.html" % n)
        if not os.path.exists(p):
            continue
        s = open(p, encoding="utf-8").read()
        s2 = re.sub(r"<b>\s*\d{1,3}\s*/\s*\d{1,3}\s*</b>", "<b>%02d / %d</b>" % (n, new_total), s)
        if s2 != s:
            open(p, "w", encoding="utf-8").write(s2)
            cnt += 1
    print("页码已重排：%d 个文件（总页数 -> %d）" % (cnt, new_total))
    print("\n下一步：")
    print("  1) 手工改章节号/交叉引用（如 2.1.4 -> 2.1.3）")
    print("  2) 重渲染 1x 与 3x（for n in 1..%d）" % new_total)
    print("  3) python replace_all_slides_pptx.py <deck> png-hi")
    print("  4) python deck_audit.py <run_dir> <deck> 复核")
    return 0


if __name__ == "__main__":
    sys.exit(main())
