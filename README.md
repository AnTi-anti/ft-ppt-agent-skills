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

## 设计思路

一句话：**把「做一份国网汇报 PPT」拆成四类文件——合同、知识、工具、样本——再规定它们各自在什么时候被读、被跑。**

### 1. 四类文件，各管一件事

| 文件 | 放什么 | 什么时候用 | 为什么放这儿 |
|---|---|---|---|
| `SKILL.md` | 触发词、五条风格合同、两条工作路径、命令、改稿速查、红线 | 任务一开始就加载 | 全是「每次都必须遵守」的，不能等到用时才想起来 |
| `references/*.md` | 版式坐标、汇报句式、CSS 片段、17 条坑、命令手册 | 按需读，一页通常只用一两份 | 细节很多，全塞进上下文会挤掉真正要做的事 |
| `scripts/*.py` | 渲染、单页 QA、整册审计、组包、删页、图内改字 | 需要精确动作时执行 | 量像素、算哈希、改文件名，脚本比模型可靠 |
| `assets/example/` | 三张成品页 | 写第一页时对照 | 一份能直接打开的样板，比十句描述管用 |

`SKILL.md` 里那张「使用前必读」的表，本质是**索引**：告诉模型「要做 X，去读 Y」，而不是把所有知识堆在一个文件里。

### 2. 一次任务实际怎么跑

```
用户："用国网汇报风格做一份 12 页汇报"
   │
   ├─ ① 触发：description 命中「国网 / 电网汇报」→ SKILL.md 进入上下文
   │
   ├─ ② 读合同：标题须为「编号 + 判断句」；内容页只有两种布局；
   │     每页一条导语；字号 ≥10px；框内不留大块空白
   │
   ├─ ③ 取细节：动笔前只读这页需要的参考
   │     坐标 → layout-spec.md ｜ 句式 → tone-guide.md
   │     组件 → css-patterns.md ｜ 会不会踩坑 → pitfalls.md
   │
   ├─ ④ 写页面：产出 slides/slide-N.html（1280×720，绝对定位）
   │
   ├─ ⑤ 渲染 + 质检：shot.py 出图 → visual_qa.py 给 PASS / WARN / FAIL
   │     模型按「哪一项 FAIL」定点修，回到 ⑤；无 FAIL 才放行
   │
   ├─ ⑥ 组包：replace_all_slides_pptx.py 把 3× 图写入 PPTX（先备份，写完回读比对）
   │
   └─ ⑦ 复核：deck_audit.py 查页码 / 尺寸 / 哈希，确认交付物与源文件一致
```

### 3. 三条设计原则

**① 把「好看」翻译成数字和断言。**
「风格统一、别太挤、字别太小」这类要求，模型每次理解都不一样。所以技能里写的是：内容区固定 `y 232–666`，左图卡 `661px` + 右栏 `525px`，正文最小 `10px`，导语条上方留白约 `18px`。有了数字，`visual_qa.py` 才能自动判定，而不是靠人盯着看。

**② 判断留给模型，精度交给脚本。**
选哪个布局、这句话怎么改、这个数字对不对——需要理解语境，交给模型；元素有没有越界、PPTX 里那张图是不是最新的、删页后页码对不对——有唯一正确答案，交给脚本。脚本不讲「大概」，所以结果可信、可重复。

**③ 每一步都留下可核对的痕迹。**
页面是 `slides/slide-N.html`，图是 `png/` 与 `png-hi/`，QA 记录是 `qa/slide-N.txt`，交付是 `deck.pptx`。谁接手、隔多久回来，都能从磁盘判断进度；`deck_audit.py` 用 sha1 回答「PPTX 里的图和源文件是不是同一张」。

### 4. 四个关键机制

**渲染：固定画布 + 3 倍超采样。**
页面写死 1280×720，`shot.py` 用 Playwright 以 `deviceScaleFactor=3` 截出 3840×2160。不用「把页面放大再截图」，因为那会连字号和留白一起放大、边缘发虚；这里只提高采样密度，布局坐标不动。截之前等 `document.fonts.ready` 与图片加载完成，避免拍到半张图。

**质检：结构 + 视觉两路。**
`visual_qa.py` 一边查 DOM——元素矩形越界、nowrap 文本溢出、卡片子元素跑出父框、标题压住页眉、导语条上方像多空一行；一边查像素——画布尺寸、墨量覆盖率、小字对比度、图片是否加载失败。输出三档：FAIL 必修，WARN 复核后可放行，PASS 直接过。

**组包：幂等 + 回读。**
`replace_all_slides_pptx.py` 假定每页正好一整幅全屏图片（本流水线的产物天然如此），按页序写入后**读回来**比对 sha1、字节数与位置，任一不符即报错；首次运行先备份 `.bak.pptx`。这样不会出现「命令成功、打开还是旧图」。

**审计：整册对齐。**
单页对了不等于整册对：`deck_audit.py` 检查 HTML 编号 1..N、每页页码 `NN / M`、3× 图尺寸、`png-hi` 是否比 HTML 旧（忘了重渲染）、PPTX 页数，以及逐页 sha1 是否与 `png-hi` 一致。

### 5. 改稿时这套设计怎么用

- **改文字**：只动 HTML → 重渲染 → QA → 组包；数字在图里的，回到绘图脚本重出图。
- **改数字**：先与实验数据 / 报告核对，`grep` 全页同名数字再改；导语、卡片、图、表必须一致。
- **删页**：`delete_slide.py` 一次完成 PPTX 删页、文件前移、页码重排；章节号等正文内容手工改。
- **老图改字**：`patch_png_text.py` 先 `--probe` 定位行带，再填底重绘，自动留 `.bak.png`。

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
