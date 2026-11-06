# -*- coding: utf-8 -*-
"""把 png-hi/slide-N.png 全屏图写回 PPTX（每页恰好 1 张满屏 picture 的结构）。

用法:
  python replace_all_slides_pptx.py <deck.pptx> <png-hi-dir>

前提: PPTX 每页只有一张 picture 形状（由 ppt-agent 的 presentation-png 管线产出）。
做备份 -> 写入 3840x2160 PNG -> 回读校验 sha1 + 尺寸 + 满屏。
"""
import hashlib
import os
import shutil
import sys

from pptx import Presentation


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    pptx, hi = sys.argv[1], sys.argv[2]
    bak = pptx.replace(".pptx", ".bak.pptx")
    if not os.path.exists(bak):
        shutil.copy2(pptx, bak)
        print("备份:", os.path.basename(bak))

    prs = Presentation(pptx)
    n_slides = len(prs.slides)
    shas = {}
    problems = []
    for i, slide in enumerate(prs.slides, 1):
        src = os.path.join(hi, f"slide-{i}.png")
        if not os.path.exists(src):
            problems.append((i, "missing png"))
            continue
        pics = [sh for sh in slide.shapes if sh.shape_type == 13]
        if len(pics) != 1:
            problems.append((i, f"{len(pics)} pictures"))
            continue
        blob = open(src, "rb").read()
        shas[i] = hashlib.sha1(blob).hexdigest()
        for rel in slide.part.rels.values():
            if rel.reltype.endswith("/image"):
                part = rel.target_part
                part._blob = blob
                part._filename = f"slide-{i}.png"
                break

    prs.save(pptx)
    print("已保存, 共", n_slides, "页")

    # 回读校验
    prs2 = Presentation(pptx)
    bad = []
    for i, slide in enumerate(prs2.slides, 1):
        if i not in shas:
            continue
        pic = [sh for sh in slide.shapes if sh.shape_type == 13][0]
        got = hashlib.sha1(pic.image.blob).hexdigest()
        size = pic.image.size
        full = (pic.left == 0 and pic.top == 0
                and pic.width == prs2.slide_width and pic.height == prs2.slide_height)
        if got != shas[i] or not full:
            bad.append((i, size, full, got == shas[i]))
    if bad:
        print("异常页:", bad)
        return 1
    print(f"校验通过: {len(shas)} 页图片匹配、满屏; 文件大小 %.1f MB" % (os.path.getsize(pptx) / 1048576))
    return 0


if __name__ == "__main__":
    sys.exit(main())
