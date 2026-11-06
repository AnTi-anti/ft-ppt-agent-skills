---
name: sgcc-report-ppt
description: 国网/电网系统正式汇报 PPT 的风格层与交付流水线。当用户要做国网、南方电网、供电公司、电力公司等单位的汇报材料（工作汇报、技术汇报、专题汇报、领导汇报、总结材料、路演/评审材料），或要求「国网风格」「电网汇报风格」「正式汇报口吻」「按我们单位模板做 PPT」时使用。也用于把已有 HTML/PPTX 改造成国网汇报风格：统一「编号+判断句」标题、左图卡+右栏布局、正式书面口吻、1280×720 HTML→PNG→PPTX 交付。与 ppt-agent（负责调研/大纲/逐页生产流程）配合使用，本技能提供其缺失的风格合同与打包脚本。
---

# 国网汇报 PPT 风格层

## 定位

本技能不是完整的 PPT 生成引擎，而是 **ppt-agent 的国网风格覆盖层 + 已验证的交付流水线**：

- **流程**（采访、调研、大纲、风格锁定、逐页 subagent）→ 由 `ppt-agent` 负责
- **风格**（布局网格、标题句式、汇报口吻、CSS 组件）→ 由本技能强制覆盖
- **交付**（Playwright 渲染、视觉 QA、PNG 组包成 PPTX）→ 本技能的 `scripts/`

若 `ppt-agent` 不可用或用户只要改造现有产物，可仅用本技能的流水线 + 规范独立完成。

## 使用前必读

| 需要做的事 | 读哪个 |
|---|---|
| 页面外壳、两种主布局、网格坐标、密度要求 | `references/layout-spec.md` |
| 正式汇报句式、禁用词、数字表述 | `references/tone-guide.md` |
| 直接抄的 CSS 片段（图卡/KPI/条形/步骤/右栏/表格） | `references/css-patterns.md` |
| 实战踩坑与修法（类名冲突、替换 MISS、图片比例…） | `references/pitfalls.md` |
| 完整命令流水线 | `references/workflow.md` |
| 安装、环境依赖、他人如何上手 | `references/install.md` |
| 可参照的成品页 | `assets/example/slide-demo-three-tier.html`（自包含，无外部图片，自检用）、`slide-4-left-fig-right-rail.html`、`slide-8-wide-fig-narrow-rail.html`、`slide-3-section-toc.html` |

## 不可协商的风格合同

生成或修改任何一页前，先确认以下五条（这是本技能存在的理由）：

1. **标题 = 「编号 + 判断句」**，如「4.2 温度输入偏差直接拉低模型精度」。禁止口语式/疑问式/口号式标题。
2. **内容页只用两种主布局**：左图卡 661px + 右栏 525px（布局 A），或宽图 927px + 窄栏 270px（布局 B）。内容区固定 y 232–666、x 39–1253。
3. **口吻是正式书面汇报**：用「随着…基于…已难以满足要求」「针对…开展…结论为…」句式；禁口语词（锅、拉下来、跟着日历走、说白了）与第一人称叙述。详见 tone-guide。
4. **每页有导语条**：导语条一句话点题 + 数据支撑，重点加粗，≤3 行。
5. **框内不留大块空白**：卡片贴合内容，或在固定框内用 flex/grid 匀开（用户明确偏好：「框不变，内容在框内匀开」）。

## 两种工作路径

### 路径 A：新做一整套（走 ppt-agent）

1. 按 `ppt-agent` 的 Step 0 采访收集需求（场景/受众/页数/资料）。
2. **在风格环节强制注入本技能合同**：Step 3.5 的 style.json 必须包含本技能的布局选择（A/B）、色彩变量、字号下限 10px、标题句式约束；Step 4 的 planning 里 `layout_hint` 只能取 `left-fig-right-rail` / `wide-fig-narrow-rail` / `toc` / `cover` / `end`。
3. 逐页 HTML 完成后，用本技能的 `scripts/` 重新渲染、QA、组包（ppt-agent 自带的导出也可用，二者产出一致）。
4. 章节结构：主目录 + 每章前插子目录页；封面不写「内部技术汇报」类字样（除非用户要求）。

### 路径 B：改造已有 HTML / PPTX

1. 先读 `references/pitfalls.md`，尤其 #1（旧 CSS 全局短类名）与 #2（文本替换 MISS）。
2. 逐页套布局 A/B 重排，类名一律加页面前缀（`.p17-kpi`）。
3. 全页文案按 `tone-guide.md` 统一为汇报口吻，**数据与事实不变**。
4. 走下方流水线渲染 → QA → 组包。

## 交付流水线（两条路径通用）

```bash
# 1. 渲染：1x 供 QA，3x 供 PPTX（PNG 必须 3840×2160）
python scripts/shot.py slides/slide-1.html png/slide-1.png 1
python scripts/shot.py slides/slide-1.html png-hi/slide-1.png 3

# 2. 视觉 QA（无 planningN.json 时可省该参数）
python scripts/visual_qa.py png/slide-1.png png/slide-1.html qa/slide-1.txt

# 2.5 整册核对：页码序列 / 文件齐全 / PPTX 是否与 3x 图同步
python scripts/deck_audit.py . deck.pptx

# 3. 组包（假定已有每页 1 张满屏图的 PPTX；首次可用 pptx 技能生成空壳）
python scripts/replace_all_slides_pptx.py deck.pptx png-hi
```

**放行标准**：每页 QA 无 `[FAIL]`（WARN 允许且常见），并逐页人工看 1× PNG。发现布局语义混乱（QA 查不出）必须重排，不能只靠脚本过关。

## 改稿与返工（实战高频）

| 场景 | 做法 |
|---|---|
| 导语条上方像"空一行" | 调 `.tpl-lede{padding-top}`；目标上方留白 ≈18px（QA 会给出 `lede spacing` 数值并 WARN） |
| 改页面上的数字 | 先与实验 JSON / 报告表格核对，`grep` 全页同名数字，再改 HTML；图里的数字改绘图脚本重出图 |
| 图内文字要改、无源脚本 | `scripts/patch_png_text.py`：`--probe` 定位行带 → `--box` + `--text` 原位替换（自动 `.bak.png`） |
| 删页 / 插页 | `scripts/delete_slide.py` 删 PPTX 页 + 文件前移 + 页码重排；章节号、交叉引用手工改，再重渲染组包 |
| 数字单位 | 不写 `pp`；绝对差写「个百分点」，本身是百分比就写「%」 |
| 用户说"打开还是旧的" | 先 `deck_audit.py` 校验；再另存新文件名排除 PowerPoint/WPS 缓存 |
| 打包报 PermissionError | PPTX 被占用：请用户关闭 PowerPoint/WPS 后重试 |

## 硬性红线

- 只改用户明确指定的页/属性；未提及的不要动。
- 新结构类名必须带页面前缀，避免与旧 CSS 撞名。
- 正文最小字号 10px；卡片子元素不得越出卡片边界；不得用 transform scale 缩放整块。
- 图片与框比例差超过约 30% 时先裁剪再嵌入，不要靠 `object-fit` 硬压。
- Windows 下运行脚本前设 `PYTHONIOENCODING=utf-8`。
- 措辞类修改**先给用户看草稿**（用户习惯：先审文字再动 PPT）；数字必须可溯源到实验数据或报告，不凭印象改。
