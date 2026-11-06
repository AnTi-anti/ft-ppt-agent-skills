# 交付流水线操作手册

> 两条路径（ppt-agent 全流程 / 改造现有产物）最后都汇入同一条流水线。所有命令在 Windows Git Bash 下验证过。

## 0. 环境前提

- Python 3 + `playwright`（Chromium 已安装）+ `python-pptx` + `Pillow`
- Windows 控制台：所有脚本用 `PYTHONIOENCODING=utf-8 python ...` 运行，或脚本内自带 `sys.stdout` UTF-8 包装

## 1. 渲染

```bash
# 单页单档
python scripts/shot.py slides/slide-1.html png/slide-1.png 1     # 1280x720, QA 用
python scripts/shot.py slides/slide-1.html png-hi/slide-1.png 3  # 3840x2160, PPTX 用

# 批量（套上循环即可）
for n in 1 2 3; do
  PYTHONIOENCODING=utf-8 python scripts/shot.py slides/slide-$n.html png/slide-$n.png 1
  PYTHONIOENCODING=utf-8 python scripts/shot.py slides/slide-$n.html png-hi/slide-$n.png 3
done
```

契约：viewport 1280×720、clip (0,0,1280,720)、`document.fonts.ready` 后截图。3× 档是 PPTX 硬要求（PowerPoint 全屏 16:9 需 3840×2160）。

## 2. QA

```bash
# 独立模式（推荐）
PYTHONIOENCODING=utf-8 python scripts/visual_qa.py png/slide-1.png slides/slide-1.html qa/slide-1.txt

# ppt-agent 兼容模式（带 planning JSON）
PYTHONIOENCODING=utf-8 python scripts/visual_qa.py png/slide-1.png planning/planning1.json slides/slide-1.html qa/slide-1.txt
```

判定：
- `status: PASS/WARN` → 通过（WARN 仅限 PNG size/very busy 两条）
- 任何 `[FAIL]` → 必须修完重跑
- QA 通过 ≠ 视觉合格：布局语义、信息密度、美观度必须人工看 1× PNG

## 3. 组包 PPTX

前提：一个每页恰好 1 张满屏 picture 的 PPTX 空壳（ppt-agent 的 `presentation-png` 产物，或用 python-pptx 建 N 页空白并各插一张满屏图）。

```bash
PYTHONIOENCODING=utf-8 python scripts/replace_all_slides_pptx.py deck.pptx png-hi
```

行为：自动备份 `.bak.pptx` → 写入 `png-hi/slide-N.png` → 回读校验 sha1 + 满屏。校验失败会列异常页并 exit 1。

页数对齐检查：`len(prs.slides)` 必须等于 `png-hi/slide-*.png` 数量，否则先补页/补图。

组包后跑一次整册核对：

```bash
python scripts/deck_audit.py <run_dir> deck.pptx
```

它会核对：HTML 编号连续、页码 `<b>NN / M</b>` 与页序一致、png/png-hi 齐全、3x 尺寸 3840×2160、PPTX 每页图片与 3x 图 sha1 一致。

## 4. 交付物清单

| 文件 | 说明 |
|---|---|
| `slides/slide-N.html` | 源文件（1280×720，可再编辑） |
| `png/slide-N.png` | 1× 截图（QA / 预览） |
| `png-hi/slide-N.png` | 3× 截图（PPTX 嵌入） |
| `deck.pptx` | 最终 PPTX |
| `deck.bak.pptx` | 组包前备份 |
| `preview.html` | iframe 预览页（可选，方便逐页过） |

## 5. 排错速查

| 现象 | 处理 |
|---|---|
| PNG 3840×2160 校验不过 | 检查 shot.py 的 scale 参数是否传 3 |
| QA 报 nowrap overflow | 加宽列或去 nowrap（pitfalls #4） |
| 改 HTML 后 PPTX 没变 | 忘了重跑 shot.py 3× 档 + 组包，两步缺一不可 |
| 组包报 "N pictures" | PPTX 空壳某页 picture 数量 ≠ 1，重建空壳 |

## 6. 改稿 / 改数 / 改图 / 删页

任何 HTML 文字改动之后，都走一遍「1x + 3x 重渲染 → 组包 → deck_audit」，三步缺一不可。

```bash
# 整册核对（页码 / 文件 / PPTX 同步）
PYTHONIOENCODING=utf-8 python scripts/deck_audit.py . deck.pptx

# 图内文字原位替换（没有绘图脚本的老图）
PYTHONIOENCODING=utf-8 python scripts/patch_png_text.py fig.png --probe --box 1300,190,1705,310
PYTHONIOENCODING=utf-8 python scripts/patch_png_text.py fig.png --box 1300,190,1705,310     --text "月电量预测76%" --size 26

# 删页（PPTX 删页 + 文件前移 + 页码重排；章节号手工改）
PYTHONIOENCODING=utf-8 python scripts/delete_slide.py deck.pptx 9 --dry-run
PYTHONIOENCODING=utf-8 python scripts/delete_slide.py deck.pptx 9
# 然后重渲染 1x/3x 并组包
```

改数三原则：
1. 以实验 JSON / 报告表格为源，先核对再改；
2. 同一数字出现在导语、卡片、图、表几处，全部 `grep` 到；
3. 图里的数字改绘图脚本重出图，不要只改页面文字。
