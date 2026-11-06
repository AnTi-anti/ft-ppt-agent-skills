<div align="center">
  <img src="assets/logo.svg" alt="sgcc-report-ppt" width="140" />
  <h1>sgcc-report-ppt</h1>
  <p>国网 / 电网系统正式汇报 PPT 的风格合同与交付流水线</p>

  <p>
    <img src="assets/badges/badge-1.svg" alt="规范：Agent Skill" />
    <img src="assets/badges/badge-2.svg" alt="版式：2 种主布局" />
    <img src="assets/badges/badge-3.svg" alt="画布：1280×720" />
    <img src="assets/badges/badge-4.svg" alt="成图：3840×2160" />
    <img src="assets/badges/badge-5.svg" alt="检查：双层 QA" />
    <img src="assets/badges/badge-6.svg" alt="脚本：6 个" />
  </p>
</div>

---

**sgcc-report-ppt** 把「国网汇报 PPT」拆成可校验的两件事：**风格合同**（标题句式、左图卡 + 右栏、正式书面口吻）与**交付流水线**（HTML → PNG → PPTX，两道质检门）。写页面的人和审页面的人，看的是同一套约束。

与 `ppt-agent` 的分工：后者负责调研、大纲、逐页生产；本技能提供它缺失的风格约束与打包脚本，也可以脱离 `ppt-agent` 单独使用——改造已有的 HTML 或 PPTX 同样适用。

## 最近更新

`2026-11-06 · v1.2`

- 新增 `deck_audit.py`：页码序列、3x 尺寸、PPTX 与 3x 图逐页 sha1 比对，一次跑完整册。
- 新增 `delete_slide.py`：PPTX 删页 + 文件前移 + 页码重排，删页不再靠手工改名。
- 新增 `patch_png_text.py`：文字烘焙进老图时的原位替换（PIL 填底 + 同字体重绘）。
- `visual_qa.py` 增加导语条留白检查："上方像空一行"从此由脚本报警，而不是靠肉眼。

## 安装

### 方式一：Agent Skills CLI（推荐，跨客户端）

```bash
npx skills add AnTi-anti/ft-ppt-agent-skills
```

常用参数（以 `npx skills --help` 为准）：

```bash
npx skills add AnTi-anti/ft-ppt-agent-skills -l      # 只预览仓库里有哪些技能
npx skills add AnTi-anti/ft-ppt-agent-skills -g -y   # 装到用户级目录，跳过确认
npx skills add AnTi-anti/ft-ppt-agent-skills --copy  # 复制文件而非软链接
```

> CLI 会自动识别 `skills/sgcc-report-ppt/SKILL.md`。npx 只装技能文件，**Python 依赖仍需单独安装**（见下）。

### 方式二：手动安装

```bash
git clone https://github.com/AnTi-anti/ft-ppt-agent-skills.git
cp -r ft-ppt-agent-skills/skills/sgcc-report-ppt ~/.claude/skills/
```

- Claude Code 个人级：`~/.claude/skills/sgcc-report-ppt`
- 项目级：`<项目>/.claude/skills/sgcc-report-ppt`

### 环境依赖

```bash
python -m pip install playwright python-pptx pillow
python -m playwright install chromium
```

安装后新开一次会话，输入 `/` 应能看到 `sgcc-report-ppt`。

## 核心亮点

**风格合同，而不是风格建议**：标题必须是「编号 + 判断句」，页面只有「左图卡 + 右栏」与「整幅图 + 窄栏」两种主布局，正文字号有下限（≥10px），导语条上下留白有目标值。每一条都写成了 `visual_qa.py` 能断言的规则，不是文档里的形容词。

**双层质检，而不是只看图**：单页 QA 同时做 DOM 断言（元素矩形、字号、nowrap 溢出、卡片包含关系）与像素断言（画布尺寸、墨量覆盖、小字对比度）。前者抓"结构越界"，后者抓"看起来发虚"。

**整册一致性可计算**：页码序列、章节号、3x 尺寸、PPTX 与 PNG 的 sha1 逐页比对，一次 `deck_audit.py` 全部给出。数字对不上、忘了重渲染，都会在交付前暴露。

**以图片为交付，跨机 100% 还原**：页面在固定 1280×720 画布上以 CSS 排定，3 倍超采样成 3840×2160，再整幅写入 PPTX。目标机器没有「微软雅黑」也不会重排——代价是文字不可再编辑，换来的是零走样。

**改稿有工具链，不靠重做**：删页有 `delete_slide.py`（PPTX 删页 + 文件前移 + 页码重排），老图改字有 `patch_png_text.py`（定位暗色行带 → 填底 → 同字体重绘），组包有幂等备份与回读校验。

**口径护栏写进流程**：同一数字只允许有一个来源；单位不写 `pp`，绝对差写「个百分点」、本身是百分比写「%」；导语、卡片、图、表、报告五处必须一致。这条约束比任何排版规则都更能减少返工。

## 实现原理

整条链路是三层 + 两道门：

```
        ┌─────────────── 版式层（HTML/CSS）───────────────┐
        │ 固定 1280×720 画布 · 绝对定位网格 · 页内前缀类名  │
        └───────────────────────┬─────────────────────────┘
                                │ shot.py（Playwright / Chromium）
                                ▼
        ┌─────────────── 光栅层（PNG）────────────────────┐
        │ 1× 供人工与 QA 检查 · 3× = 3840×2160 供交付      │
        └───────────────────────┬─────────────────────────┘
                    视觉门 ◄─────┤ visual_qa.py（DOM + 像素）
                                ▼
        ┌─────────────── 组装层（PPTX）───────────────────┐
        │ 每页一整幅全屏图片 · 备份 · sha1 回读 · 整册审计  │
        └─────────────────────────────────────────────────┘
```

### 1. 为什么以 HTML 为源

PPT 的对象模型不适合做精确排版：字体替换、文本框自动换行、行距吸附都会让"在我机器上刚好"变成"在会议室里溢出两行"。HTML/CSS 则可以把每个元素钉在像素坐标上——`1280×720` 的 `body`、`overflow:hidden`、绝对定位的主区、`grid` 分栏、固定的字号阶梯。这让版式从"调参"变成"写约束"。

代价是文字不可编辑，因此约定：**HTML 是唯一真源，PPTX 是它的渲染产物**。要改字，改 HTML 重出图；要改图里的字（老素材），用 `patch_png_text.py`。

### 2. 光栅化：固定画布 + 超采样

`shot.py` 做四件事：

| 步骤 | 做法 | 为什么 |
|---|---|---|
| 视口 | `viewport = 1280×720`，`deviceScaleFactor = scale` | 布局坐标系恒定，缩放只影响采样密度 |
| 等待 | `document.fonts.ready` + 图片 `complete` | 避免字体回退或半张图被拍下来 |
| 截图 | 整页 `screenshot`，`clip` 到画布 | 不裁不拼，坐标与 CSS 一一对应 |
| 输出 | 1× 供 QA，3× = 3840×2160 供 PPTX | 3× 在 16:9 投影与打印下都不掉细节 |

之所以不用 `transform: scale()` 放大页面再截图：那会让字号与留白一起被放大，QA 的量测全部失真，且圆角、边框会出现半像素模糊。`visual_qa.py` 因此把 `transform scale` 视为 FAIL。

### 3. 单页质检：DOM 断言 + 像素断言

`visual_qa.py` 把"好看"翻译成两类可判定问题：

| 类别 | 检查项 | 判定方式 |
|---|---|---|
| 结构 | 画布尺寸、页面溢出、文本越界 | `body` 与元素的 `getBoundingClientRect()` |
| 结构 | nowrap 文本溢出 | 元素 `scrollWidth > clientWidth` |
| 结构 | 卡片子元素越界 | `[data-card-id]` 内子元素矩形必须落在父框内 |
| 结构 | 标题与页眉元信息重叠 | 两个矩形相交判定（重叠 → WARN） |
| 结构 | 导语条留白 | 导语 `top` 与 `bottom` 间距对比，识别"上方像空一行" |
| 视觉 | 最小字号、墨量覆盖、小字对比度 | DOM 取字号；PIL 统计非背景像素与局部对比度 |
| 视觉 | 外部图片缺失 | `img` 的 `naturalWidth === 0` 直接 FAIL |

判定结果是三档：`PASS` / `WARN` / `FAIL`。**WARN 允许放行，FAIL 必须修**——把"已知误报"和"真问题"分开，才不会让人习惯性忽略告警。

### 4. 整册审计：把"忘了重渲染"变成可计算的事

单页正确不等于整册正确。`deck_audit.py` 用四组规则把整册对齐：

1. `slides/slide-N.html` 必须从 1 连续到 N；
2. 每页页码 `<b>NN / M</b>` 的 NN 等于页序、M 等于总页数；
3. `png/` 与 `png-hi/` 每页都有图，且 `png-hi` 必须是 3840×2160；
4. `png-hi` 的修改时间早于 HTML → 提示"忘了重渲染"；传入 PPTX 时，逐页比对 PPTX 内嵌图片与 `png-hi` 的 **sha1**。

第 4 条是关键：交付物与源文件是否同步，不再靠记忆，而是靠哈希。删页、重排、改数之后，只要有一处没重跑，审计就会指出具体页号。

### 5. 组包：幂等、可回读、可回退

`replace_all_slides_pptx.py` 的前提是"每页恰好一整幅全屏图片"（本流水线的产物天然满足）。它按页序把 `png-hi/slide-N.png` 写入对应页，然后：

- 首次运行先把 PPTX 备份为 `.bak.pptx`（已存在则不覆盖）；
- 写完后**回读**每页图片，比对 sha1、字节数与全幅位置；
- 任一项不符即报错退出，不产生"看起来成功但其实是旧图"的假交付。

配合 `deck_audit.py`，组包的正确性有两道独立验证：写入端自检 + 审计端复核。

### 6. 改稿：删页与图内改字

**删页**（`delete_slide.py`）：PPTX 的 `sldIdLst` 删一项，磁盘上 `slide-K.*` 三个文件删除、K+1..N 整体前移、所有 `<b>NN / M</b>` 重写为新页序与新的总页数。章节号与交叉引用属于内容，脚本不猜，改完重渲染即可。

**图内改字**（`patch_png_text.py`）：先用 `--probe` 扫出指定区域里的暗色行带（拿到 y 起止与 x 范围），再用 `--box` 填背景色、按同字体字号居中重绘。自动留 `.bak.png`，文字超出框会提示。适用于没有绘图脚本的老图，新图应回到绘图脚本里改。

### 7. 口径护栏

排版错误肉眼能看见，口径错误往往看不见。因此把三条规则前移到流程里：

- **单一来源**：同一数字只允许来自实验 JSON / 报告表，改一处必须 `grep` 全页同名数字；
- **单位规范**：不写 `pp`；绝对差写「个百分点」，本身是百分比写「%」；斜杠表述（`81.31% / 82.81%`）必须标注顺序（工作日 / 周末）；
- **五处一致**：导语、卡片、图、表、报告里的同一个数必须相同，图里的数字改完要重出图。

## 工作流

```
读需求 → 定页面清单（编号 + 判断句标题）
  → 逐页 HTML（版式 A：左图卡 + 右栏 / 版式 B：整幅图 + 窄栏）
  → 1× 渲染 → visual_qa.py（FAIL 必修，WARN 复核）
  → 3× 渲染 → replace_all_slides_pptx.py（备份 + 回读校验）
  → deck_audit.py（页码 / 尺寸 / sha1 全册复核）
  → 逐页人工看 1× PNG（布局语义与信息密度，脚本查不出）
```

## 产物链

```
slides/slide-N.html
  → png/slide-N.png            # 1×，1280×720
  → png-hi/slide-N.png         # 3×，3840×2160
  → qa/slide-N.txt             # 单页 QA 记录
  → deck.pptx                  # 逐页全幅图片
  → deck.bak.pptx              # 组包前备份
```

## 效果示例

<div align="center">
  <img src="assets/screenshots/demo-three-tier.png" width="92%" alt="版式示例：左图卡 + 右栏" />
</div>

> 示例页源码：`assets/demo/slide-demo-three-tier.html`，可直接 `python scripts/shot.py` 复现，也可作为版式起点改写。

## 快速开始

本项目以 Agent Skill 形式运行，无需独立部署。在支持 Skill 的客户端中输入需求即可触发：

> *"用国网汇报风格做一份 12 页的配网负荷预测方法汇报，标题用编号 + 判断句，重点讲三段闭环。"*

也可以直接对已有材料说：

> *"把这份 22 页 PPT 改成国网汇报风格，去掉来源标注，导语条上面不要空一行。"*

技能会按流水线逐页渲染、QA、组包，产物落在 `ppt-output/runs/<RUN_ID>/`。

## 仓库结构

```
ft-ppt-agent-skills/
├── README.md
└── skills/
    └── sgcc-report-ppt/
        ├── SKILL.md              # 主入口：风格合同、两条路径、流水线、改稿速查、红线
        ├── references/           # 版式规范、口吻指南、CSS 组件、17 条坑与修法、命令手册
        ├── scripts/              # 渲染 / 单页 QA / 整册审计 / 组包 / 删页 / 图内改字
        └── assets/example/       # 三张成品页样例（可直接渲染对照）
```

| 脚本 | 作用 |
|---|---|
| `scripts/shot.py` | `shot.py <html> <png> <scale>`：1× 供 QA，3× 供 PPTX |
| `scripts/visual_qa.py` | 单页 QA：结构与像素十余项检查，输出 PASS / WARN / FAIL |
| `scripts/deck_audit.py` | 整册审计：编号、页码、尺寸、stale、PPTX sha1 |
| `scripts/replace_all_slides_pptx.py` | 把 `png-hi/` 写回 PPTX，备份 + 回读校验 |
| `scripts/delete_slide.py` | 删页：PPTX 删页 + 文件前移 + 页码重排 |
| `scripts/patch_png_text.py` | 图片内文字原位替换（老素材专用） |

## 客户端兼容性

| 客户端 | 安装方式 | 说明 |
|---|---|---|
| Claude Code | `npx skills add` / 手动复制 | 完整支持技能自动加载与 `/` 触发 |
| 其他实现 Agent Skills 的客户端 | `npx skills add` | 取决于客户端是否实现 SKILL.md 规范 |
| 仅支持规则文件（AGENTS.md / rules）的客户端 | 手动 | 把 `SKILL.md` 作为规则喂入，`scripts/` 照常调用 |
| 内网 / 离线环境 | 离线包 | 复制 `skills/sgcc-report-ppt` 到技能目录即可 |

> `scripts/` 全部是纯 Python（Playwright / python-pptx / Pillow），不依赖任何特定 AI 客户端；差异只在"是否自动发现技能"。

## 常见问题

| 现象 | 处理 |
|---|---|
| 中文输出报 `UnicodeEncodeError` | 加 `PYTHONIOENCODING=utf-8`（打包类脚本用 `PYTHONUTF8=1`） |
| Playwright 找不到浏览器 | `python -m playwright install chromium` |
| 组包报 `PermissionError ... .pptx` | PPTX 被 PowerPoint / WPS 占用，关闭后重跑 |
| QA 报 `nowrap text overflow` | 加宽列或去掉 `nowrap`（见 `references/pitfalls.md` #4） |
| 用户说"打开还是旧的" | 先跑 `deck_audit.py` 校验，再另存新文件名排除软件缓存 |
| 渲染字体不对 | 系统缺「微软雅黑」，安装字体后重启终端 |

## 致谢

版式与流水线的设计参考了 [ppt-agent-skills](https://github.com/sunbigfly/ppt-agent-skills) 的工程化思路：把演示文稿生产当成可校验的构建过程。两者可配合使用——`ppt-agent` 管流程，本技能管风格与交付。
