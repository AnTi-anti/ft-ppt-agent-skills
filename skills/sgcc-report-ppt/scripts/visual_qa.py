#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""国网汇报 PPT 单页视觉 QA（不依赖 planningN.json）。

用法:
  python visual_qa.py <slide.png> <slide.html> [out.txt]
  python visual_qa.py <slide.png> <planningN.json> <slide.html> [out.txt]   # ppt-agent 兼容

检查项:
  画布 1280x720 / 无滚动溢出 / 最小字号 10px / nowrap 溢出 / 文字越界 /
  卡片子元素越界 / 图片加载 / transform scale / 墨水覆盖率 / 小字对比度 /
  标题与右上元信息重叠 / 导语条上下留白是否失衡（上方像空一行）

退出码: 0 PASS, 2 WARN, 1 FAIL
"""
import json
import os
import re
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

from _browser import open_browser


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        return 2
    png = args[0]
    plan = None
    if args[1].endswith(".json"):
        plan = json.load(open(args[1], encoding="utf-8")).get("page")
        html = args[2]
        out = args[3] if len(args) > 3 else None
    else:
        html = args[1]
        out = args[2] if len(args) > 2 else None

    fails, warns, oks = [], [], []

    def ok(m): oks.append(m)
    def fail(m): fails.append(m)
    def warn(m): warns.append(m)

    # ---------- pixel ----------
    if not os.path.exists(png):
        fail("PNG missing: %s" % png)
    else:
        im = Image.open(png).convert("RGB")
        w, h = im.size
        if (w, h) != (1280, 720):
            warn("PNG size %dx%d (expected 1280x720)" % (w, h))
        else:
            ok("PNG size 1280x720")
        px = im.load()
        total = ((h + 1) // 2) * ((w + 1) // 2)
        nonwhite = 0
        for y in range(0, h, 2):
            for x in range(0, w, 2):
                r, g, b = px[x, y]
                if r < 245 or g < 245 or b < 245:
                    nonwhite += 1
        ratio = nonwhite / float(total)
        if ratio < 0.03:
            fail("PNG near-blank: non-white ratio %.3f < 0.03" % ratio)
        elif ratio > 0.65:
            warn("PNG very busy: non-white ratio %.3f" % ratio)
        else:
            ok("ink coverage %.1f%%" % (ratio * 100))
        if os.path.getsize(png) < 15000:
            fail("PNG suspiciously small (%d bytes)" % os.path.getsize(png))

    # ---------- DOM ----------
    with sync_playwright() as p:
        b = open_browser(p, quiet=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 720})
        pg = ctx.new_page()
        pg.goto("file:///" + os.path.abspath(html).replace("\\", "/"), wait_until="load")
        pg.wait_for_timeout(300)

        dims = pg.evaluate("""() => {
            const b=document.body;
            return {bw:b.getBoundingClientRect().width, bh:b.getBoundingClientRect().height,
                    sw:document.documentElement.scrollWidth, sh:document.documentElement.scrollHeight};
        }""")
        if dims["bw"] != 1280 or dims["bh"] != 720:
            fail("body is %sx%s, expected 1280x720" % (dims["bw"], dims["bh"]))
        else:
            ok("body is 1280x720")
        if dims["sw"] > 1280 or dims["sh"] > 720:
            fail("document scroll size %sx%s exceeds 1280x720 (clipping risk)" % (dims["sw"], dims["sh"]))
        else:
            ok("no page overflow / scroll")

        # planning card presence (only when plan given)
        if plan:
            card_ids = [c["card_id"] for c in plan.get("cards", [])]
            present = pg.evaluate("""(ids) => ids.map(id => {
                const els=document.querySelectorAll('[data-card-id="'+id+'"]');
                if(!els.length) return {id, n:0};
                const r=els[0].getBoundingClientRect();
                return {id, n:els.length, w:r.width, h:r.height};
            })""", card_ids)
            for c in present:
                if c["n"] == 0:
                    fail("planning card missing in HTML: %s" % c["id"])
                elif c["n"] > 1:
                    warn("duplicate data-card-id: %s x%d" % (c["id"], c["n"]))
                else:
                    ok("card %s present (%.0fx%.0f)" % (c["id"], c["w"], c["h"]))

        # transform scale
        scale_hits = pg.evaluate("""() => {
            const bad=[];
            document.querySelectorAll('body *').forEach(el=>{
                if(el.closest('svg')) return;
                const t=getComputedStyle(el).transform;
                if(t && t!=='none'){
                    const mm=t.match(/matrix\\(([^)]+)\\)/);
                    if(mm){
                        const m=mm[1].split(',').map(Number);
                        const sx=Math.hypot(m[0],m[1]), sy=Math.hypot(m[2],m[3]);
                        if(Math.abs(sx-1)>0.05 || Math.abs(sy-1)>0.05){
                            bad.push(el.tagName+'.'+(typeof el.className==='string'?el.className:''));
                        }
                    }
                }
            });
            return bad;
        }""")
        if scale_hits:
            fail("transform scale detected on: %s" % ", ".join(scale_hits))
        else:
            ok("no transform scale hack")

        # font size / nowrap overflow / outside canvas
        stats = pg.evaluate("""() => {
            const out={minFont:999,minText:'',tiny:[],overflow:[],outside:[]};
            const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
            let n;
            while(n=walker.nextNode()){
                if(!n.textContent.trim()) continue;
                const el=n.parentElement, cs=getComputedStyle(el);
                if(cs.display==='none'||cs.visibility==='hidden') continue;
                const fs=parseFloat(cs.fontSize), txt=n.textContent.trim().slice(0,24);
                if(fs<out.minFont){out.minFont=fs;out.minText=txt;}
                if(fs<10) out.tiny.push(txt+' @'+fs.toFixed(1)+'px');
                const r=el.getBoundingClientRect();
                if(r.width>0 && r.height>0){
                    if(r.left<0||r.top<0||r.right>1280.5||r.bottom>720.5)
                        out.outside.push(txt+' @'+Math.round(r.left)+','+Math.round(r.top));
                    if(el.scrollWidth > el.clientWidth+2 && cs.whiteSpace==='nowrap')
                        out.overflow.push(txt+' sw'+el.scrollWidth+'>cw'+el.clientWidth);
                }
            }
            return out;
        }""")
        if stats["minFont"] < 10:
            fail("text below 10px: %s (%s)" % (stats["minFont"], ", ".join(stats["tiny"][:5])))
        else:
            ok("min text size %.1fpx ('%s')" % (stats["minFont"], stats["minText"]))
        if stats["overflow"]:
            fail("nowrap text overflow: %s" % "; ".join(stats["overflow"][:5]))
        else:
            ok("no nowrap text overflow")
        if stats["outside"]:
            fail("text outside canvas: %s" % "; ".join(stats["outside"][:5]))
        else:
            ok("all text inside 1280x720")

        # card children containment
        outside = pg.evaluate("""() => {
            const bad=[];
            document.querySelectorAll('[data-card-id]').forEach(card=>{
                const cr=card.getBoundingClientRect();
                card.querySelectorAll('*').forEach(el=>{
                    if(el.closest('svg')) return;
                    const r=el.getBoundingClientRect();
                    if(r.width===0||r.height===0) return;
                    if(r.left<cr.left-0.6||r.right>cr.right+0.6||r.top<cr.top-0.6||r.bottom>cr.bottom+0.6)
                        bad.push(card.getAttribute('data-card-id')+':'+(el.className||el.tagName));
                });
            });
            return bad;
        }""")
        if outside:
            fail("elements exceed card bounds: %s" % "; ".join(sorted(set(outside))[:8]))
        else:
            ok("all card children contained in card bounds")

        # content-area bounds (layout library L1-L8 must stay inside y 232-666)
        zone = pg.evaluate("""() => {
            const bad=[], early=[];
            let maxBottom=0, maxDesc='';
            document.querySelectorAll('body *').forEach(el=>{
                if(el.closest('svg')) return;
                const cs=getComputedStyle(el);
                if(cs.display==='none'||cs.visibility==='hidden') return;
                const tag=el.tagName.toLowerCase();
                if(tag==='html'||tag==='body') return;
                const r=el.getBoundingClientRect();
                if(r.width<=0||r.height<=0) return;
                const desc=tag+(typeof el.className==='string'&&el.className?'.'+el.className.trim().split(/\\s+/)[0]:'');
                if(r.top>=666) return;              // 页脚及以下：不是内容
                if(r.top<232){                      // 外壳区域：只看是否下探进内容区
                    if(r.top>=218 && r.top<226 && r.height>8 && r.width>100) early.push(desc+' top='+Math.round(r.top));
                    return;
                }
                if(r.bottom>maxBottom){maxBottom=r.bottom;maxDesc=desc;}
                if(r.bottom>680) bad.push(desc+' bottom='+Math.round(r.bottom));
            });
            return {maxBottom:Math.round(maxBottom),maxDesc,bad:bad.slice(0,5),early:early.slice(0,3)};
        }""")
        if zone["bad"]:
            fail("content exceeds y=680 (overlaps footer): %s" % "; ".join(zone["bad"]))
        elif zone["maxBottom"] > 667:
            warn("content ends at y=%d, tighter than the 666 grid (footer starts 686)" % zone["maxBottom"])
        else:
            ok("content inside y 232-666 (lowest %dpx: %s)" % (zone["maxBottom"], zone["maxDesc"]))
        if zone["early"]:
            warn("content starts below y=218 / above 226 (overlaps lede gap): %s" % "; ".join(zone["early"]))

        # title vs header meta overlap
        overlap = pg.evaluate("""() => {
            const a=document.querySelector('.page-title'), b=document.querySelector('.hdr-meta, .header-meta');
            if(!a||!b) return null;
            const ra=a.getBoundingClientRect(), rb=b.getBoundingClientRect();
            const w=Math.min(ra.right,rb.right)-Math.max(ra.left,rb.left);
            const h=Math.min(ra.bottom,rb.bottom)-Math.max(ra.top,rb.top);
            return (w>0&&h>0)?{w,h}:{w:0,h:0};
        }""")
        if overlap and overlap["w"] > 0 and overlap["h"] > 0:
            warn("page-title box overlaps header meta by %.0fx%.0f (verify visually)" % (overlap["w"], overlap["h"]))
        else:
            ok("title does not collide with header meta")

        # lede vertical spacing (blank-line-above symptom)
        lede = pg.evaluate("""() => {
            const el=document.querySelector('.tpl-lede');
            if(!el) return null;
            const cs=getComputedStyle(el), r=el.getBoundingClientRect();
            const rg=document.createRange(); rg.selectNodeContents(el);
            const rt=rg.getBoundingClientRect();
            const bt=parseFloat(cs.borderTopWidth)||0, bb=parseFloat(cs.borderBottomWidth)||0;
            return {top:+(rt.top-r.top-bt).toFixed(1), bottom:+(r.bottom-rt.bottom-bb).toFixed(1)};
        }""")
        if lede:
            if lede["top"] >= 28 or (lede["top"] - lede["bottom"]) >= 12:
                warn("lede top gap %.0fpx vs bottom %.0fpx (looks like a blank line above; set .tpl-lede padding-top ~16px)"
                     % (lede["top"], lede["bottom"]))
            else:
                ok("lede spacing balanced (top %.0f / bottom %.0f)" % (lede["top"], lede["bottom"]))

        # images
        imgs = pg.evaluate("""() => Array.from(document.images).map(i=>({src:i.getAttribute('src'),ok:i.naturalWidth>0}))""")
        if imgs:
            bad = [i["src"] for i in imgs if not i["ok"]]
            if bad:
                fail("broken images: %s" % ", ".join(bad))
            else:
                ok("images loaded (%d)" % len(imgs))
        else:
            ok("no external images")

        # contrast of small text
        small = pg.evaluate("""() => {
            const out=[], seen=new Set();
            const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
            let n;
            while(n=walker.nextNode()){
                if(!n.textContent.trim()) continue;
                const el=n.parentElement, cs=getComputedStyle(el), fs=parseFloat(cs.fontSize);
                if(fs>=12) continue;
                const key=cs.color+'|'+el.className;
                if(seen.has(key)) continue; seen.add(key);
                out.push({c:cs.color, cls:el.className, t:n.textContent.trim().slice(0,12)});
            }
            return out;
        }""")

        def lum(c):
            m = re.match(r"rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)", c)
            if not m:
                return None
            rgb = [float(x) / 255 for x in m.groups()[:3]]
            rgb = [(x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4) for x in rgb]
            return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]

        low = []
        for s in small:
            L = lum(s["c"])
            if L is None:
                continue
            cr = 1.05 / (L + 0.05)
            if cr < 3.0:
                low.append("%s(%.1f:1 %s)" % (s["t"], cr, s["cls"]))
        if low:
            warn("small text contrast <3:1: %s" % ", ".join(low[:6]))
        else:
            ok("small text contrast >=3:1")

        b.close()

    status = "FAIL" if fails else ("WARN" if warns else "PASS")
    lines = ["visual_qa (sgcc-report-ppt)", "page: %s" % (plan.get("slide_number") if plan else os.path.basename(html)),
             "status: %s" % status, "", "[PASS] %d checks" % len(oks)]
    lines += ["  + " + m for m in oks]
    if warns:
        lines += ["", "[WARN] %d" % len(warns)] + ["  ! " + m for m in warns]
    if fails:
        lines += ["", "[FAIL] %d" % len(fails)] + ["  x " + m for m in fails]
    text = "\n".join(lines)
    print(text)
    if out:
        open(out, "w", encoding="utf-8").write(text + "\n")
    return 1 if fails else (2 if warns else 0)


if __name__ == "__main__":
    sys.exit(main())
