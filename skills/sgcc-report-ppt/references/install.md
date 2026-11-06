# sgcc-report-ppt 技能：安装与使用说明

> 适用对象：需要使用本技能制作/改造「国网（电网）汇报 PPT」的同事
> 配套文件：`sgcc-report-ppt.skill`（技能分发包，本质是一个 zip）
> 版本：v1.2 ｜ 2026-11-06

---

## 0. 一键安装（推荐）

在 `skill-new` 目录下，**一条命令**即可完成「复制技能 + 安装依赖 + 自检」：

```bash
python install.py
```

- **Windows**：直接**双击 `install.bat`**（或在目录里运行 `python install.py`）
- **macOS / Linux**：`bash install.sh`（或 `python3 install.py`）

脚本会依次完成：

1. 检查 Python 版本（≥3.9）；
2. 把技能复制到 `~/.claude/skills/sgcc-report-ppt`（已存在则先备份为 `.bak-时间戳`）；
3. `pip install playwright python-pptx pillow` + `playwright install chromium`；
4. 渲染示例页做一次自检，输出 `status: WARN`（无 FAIL）即安装成功。

常用参数：

```bash
python install.py --no-deps     # 依赖已装过，跳过 pip/Chromium
python install.py --no-test     # 跳过自检
python install.py --project     # 装到当前项目的 .claude/skills（而非个人目录）
python install.py -y            # 覆盖旧版本时不再询问
```

安装完成后**重启 Claude Code**（或新开会话），输入 `/` 应能看到 `sgcc-report-ppt`。

> 说明：Claude Code 目前没有类似 `npm install` 的技能仓库，个人技能就是 `~/.claude/skills/` 下的文件夹；本脚本把「解压 + 放对位置 + 装依赖 + 自检」合成了一步，等同于 npm 式安装的体验。

## 0.2 通过 npx skills 安装（跨客户端，已发布）

技能已发布到 Git 仓库：**https://github.com/AnTi-anti/ft-ppt-agent-skills**

任何支持 Agent Skills 的 AI 客户端，一条命令即可安装：

```bash
npx skills add AnTi-anti/ft-ppt-agent-skills
```

常用参数（实测于 skills CLI，最新参数以 `npx skills --help` 为准）：

| 参数 | 作用 |
|---|---|
| `-l` | 只列出仓库里有哪些技能，不安装 |
| `-g -y` | 装到用户级目录，跳过确认 |
| `--copy` | 复制文件而不是软链接 |
| `-a <agent>` | 指定客户端；`--all` = 全部客户端 |

说明：

- 仓库结构为 `skills/sgcc-report-ppt/SKILL.md`，CLI 可直接发现（`Found 1 skill`）；
- **npx 只装技能文件，不装 Python 依赖**，装完仍需执行第 2 节的 `pip install ...` 与 `playwright install chromium`；
- 需要能访问 npm registry 与 GitHub；内网受限时改用第 0 节的离线安装方式；
- **客户端支持程度**：实现了 Agent Skills（SKILL.md）规范的客户端可自动安装并触发；只支持规则文件的客户端，可把 SKILL.md 当作规则喂入；无论哪种，`scripts/` 里的 Python 脚本与客户端无关，照常可用。

## 0.1 手动安装（备选，5 步）

1. **安装并登录 Claude Code**（桌面版或 `npm i -g @anthropic-ai/claude-code`）。
2. **安装 Python 依赖**（Python 3.9+）：

   ```bash
   python -m pip install playwright python-pptx pillow
   python -m playwright install chromium
   ```

3. **解压技能包**到技能目录（保证 `...\skills\sgcc-report-ppt\SKILL.md` 层级）：

   ```powershell
   # Windows PowerShell
   Expand-Archive .\sgcc-report-ppt.skill -DestinationPath "$env:USERPROFILE\.claude\skills" -Force
   ```

   ```bash
   # macOS / Linux / Git Bash
   unzip sgcc-report-ppt.skill -d ~/.claude/skills
   ```

4. **重启 Claude Code（或新开会话）**，输入 `/`，列表中应出现 `sgcc-report-ppt`。
5. **自检**（在技能目录下执行）：

   ```bash
   cd ~/.claude/skills/sgcc-report-ppt
   python scripts/shot.py assets/example/slide-3-section-toc.html demo.png 1
   python scripts/visual_qa.py demo.png assets/example/slide-3-section-toc.html
   ```

   预期 `status: WARN` 且包含 `lede spacing balanced (top 18 / bottom 16)`；**只要没有 `[FAIL]` 即安装成功**。

> 新机器常见坑：忘了 `playwright install chromium`；`python` 未加入 PATH；技能目录多套了一层文件夹；中文报错未设 `PYTHONIOENCODING=utf-8`。详见第 7 节。

---

## 1. 这是什么

`sgcc-report-ppt` 是**国网汇报 PPT 的风格层 + 交付流水线**，不是一个独立的 PPT 生成引擎：

- **风格合同**：标题「编号 + 判断句」、左图卡 + 右栏两种主布局、正式书面口吻、1280×720 画布；
- **交付流水线**：HTML 幻灯片 → Playwright 渲染（1× 供检查、3× 供出图）→ 视觉 QA → 组包成 PPTX；
- **配套脚本**：单页 QA、整册核对、删页重排、图片内文字替换、PPTX 组包。

它与 `ppt-agent`（负责需求调研、大纲、逐页生产）配合使用：ppt-agent 管流程，本技能管风格与交付；也可以单独用来改造已有的 HTML / PPTX。

---

## 2. 环境要求

| 项 | 要求 |
|---|---|
| Claude Code | 能加载个人或项目技能目录 |
| Python | 3.9 及以上 |
| Python 包 | `playwright`、`python-pptx`、`Pillow` |
| 浏览器 | Playwright 的 Chromium |
| 字体 | 页面用「微软雅黑」；处理 Word 类材料需「方正仿宋_GBK」（可选） |

安装依赖：

```bash
pip install playwright python-pptx pillow
python -m playwright install chromium
```

Windows 控制台建议先设置 UTF-8，避免中文输出报错：

```bash
export PYTHONIOENCODING=utf-8      # Git Bash
# PowerShell: $env:PYTHONIOENCODING="utf-8"
```

---

## 3. 安装技能

`.skill` 文件本质是 zip 包，解压后是一个同名文件夹，**SKILL.md 必须位于文件夹根目录**。

### 方式一：从 .skill 包安装（推荐）

**Windows PowerShell**

```powershell
Expand-Archive -Path .\sgcc-report-ppt.skill -DestinationPath $env:USERPROFILE\.claude\skills
```

**Git Bash / macOS / Linux**

```bash
unzip sgcc-report-ppt.skill -d ~/.claude/skills
```

解压后目录应为：

```
~/.claude/skills/sgcc-report-ppt/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

### 方式二：直接拷贝文件夹

把 `sgcc-report-ppt` 整个文件夹放到：

- **个人级（所有项目可用）**：`~/.claude/skills/`
- **项目级（仅当前项目）**：`<项目根目录>/.claude/skills/`

### 生效与确认

1. **重启 Claude Code 或新开一个会话**（技能在会话启动时加载）；
2. 在输入框输入 `/`，列表中应出现 `sgcc-report-ppt`；
3. 也可以直接说「用国网汇报风格做一份 PPT」，Claude 会自动调用。

### 安装自检（可选，但建议做一次）

```bash
cd ~/.claude/skills/sgcc-report-ppt
python scripts/shot.py assets/example/slide-3-section-toc.html /tmp/demo.png 1
python scripts/visual_qa.py /tmp/demo.png assets/example/slide-3-section-toc.html
```

预期输出：

```
status: WARN
  + lede spacing balanced (top 18 / bottom 16)
  ...（可能有一条 page-title 与页眉元信息重叠的 WARN，属已知误报）
```

只要没有 `[FAIL]`，就说明渲染、浏览器、脚本都正常。

---

## 4. 目录结构与各文件用途

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 技能入口：风格合同、两条工作路径、流水线、改稿速查表、红线 |
| `references/layout-spec.md` | 页面外壳、布局 A/B、网格坐标、密度要求 |
| `references/tone-guide.md` | 正式汇报句式、禁用词、数字表述 |
| `references/css-patterns.md` | 可直接抄用的 CSS 组件（图卡、KPI、条形、步骤、右栏、表格） |
| `references/pitfalls.md` | 17 条实战坑与修法（类名冲突、图片文字、页码、口径一致性…） |
| `references/workflow.md` | 完整命令手册（渲染、QA、组包、改稿、删页、排错） |
| `scripts/shot.py` | 渲染：`shot.py <html> <png> <scale>`，scale=1 供 QA，3 供 PPTX |
| `scripts/visual_qa.py` | 单页 QA：画布、字号、nowrap 溢出、卡片越界、对比度、导语留白等 |
| `scripts/deck_audit.py` | 整册核对：页码序列、文件齐全、3x 尺寸、PPTX 是否与图同步 |
| `scripts/replace_all_slides_pptx.py` | 把 `png-hi/slide-N.png` 写回 PPTX（先备份、后回读校验） |
| `scripts/delete_slide.py` | 删页：PPTX 删页 + 文件前移 + 页码重排（章节号手工改） |
| `scripts/patch_png_text.py` | 图片内文字原位替换（无绘图脚本的老图） |
| `assets/example/*.html` | 三张成品页样例，可直接渲染对照 |

---

## 5. 怎么用

### 路径 A：从零做一套（推荐配合 ppt-agent）

1. 对 Claude 说明需求：「做一份国网汇报 PPT，主题…受众…页数…」，触发 `ppt-agent` 主持流程；
2. 风格环节由本技能强制约束：标题句式、布局 A/B、导语条、字号下限、正式口吻；
3. 逐页 HTML 完成后，用本技能脚本渲染、QA、组包。

### 路径 B：改造已有 HTML / PPTX

1. 先读 `references/pitfalls.md`（尤其是旧 CSS 全局短类名、文本替换 MISS 两条）；
2. 按布局 A/B 重排，新结构的类名一律加页面前缀（如 `.p17-kpi`）；
3. 文案统一为汇报口吻（数据与事实不变）；
4. 走下面的流水线。

### 交付流水线（两条路径通用）

```bash
# 1) 渲染：1x 供 QA，3x 供 PPTX（3x = 3840×2160，PPTX 硬要求）
python scripts/shot.py slides/slide-1.html png/slide-1.png 1
python scripts/shot.py slides/slide-1.html png-hi/slide-1.png 3

# 2) 单页 QA：无 FAIL 才放行（WARN 允许）
python scripts/visual_qa.py png/slide-1.png slides/slide-1.html qa/slide-1.txt

# 3) 组包：把 3x 图写回 PPTX（自动备份 + 回读校验）
python scripts/replace_all_slides_pptx.py deck.pptx png-hi

# 4) 整册核对：页码 / 文件 / 尺寸 / PPTX 是否逐页同步
python scripts/deck_audit.py . deck.pptx
```

**放行标准**：`visual_qa.py` 无 `[FAIL]`，`deck_audit.py` 为 `PASS` 或仅 WARN，并逐页人工看 1× PNG（布局语义、信息密度 QA 查不出）。

---

## 6. 改稿 / 改数 / 改图 / 删页 速查

| 场景 | 做法 |
|---|---|
| 导语条上方像"空一行" | 调 `.tpl-lede{padding-top}`，目标上方留白约 18px；QA 会给出 `lede spacing` 数值并提示 |
| 改页面数字 | 先与实验数据/报告核对，再 `grep` 全页同名数字，最后改 HTML；数字在图里的要改绘图脚本重出图 |
| 图内文字要改、又没有绘图脚本 | `python scripts/patch_png_text.py fig.png --probe --box x1,y1,x2,y2` 定位行带，再用 `--box/--text/--size` 替换（自动 `.bak.png`） |
| 删页 | `python scripts/delete_slide.py deck.pptx 9 --dry-run` 先看计划，去掉 `--dry-run` 执行；之后手工改章节号，重渲染、重新组包 |
| 数字单位 | 不写 `pp`；绝对差写「个百分点」，本身是百分比就写「%」 |
| 用户说"打开还是旧的" | 先跑 `deck_audit.py` 校验；再另存新文件名让用户打开，排除 PowerPoint/WPS 缓存 |

---

## 7. 常见问题

| 现象 | 处理 |
|---|---|
| 中文输出报 `UnicodeEncodeError` | 运行时加 `PYTHONIOENCODING=utf-8`；打包类脚本可用 `PYTHONUTF8=1` |
| Playwright 报找不到浏览器 | `python -m playwright install chromium` |
| 组包时报 `PermissionError ... .pptx` | PPTX 被 PowerPoint/WPS 占用，关闭后再跑 |
| QA 报 `nowrap text overflow` | 加宽所在列/容器，或去掉 `nowrap`（见 pitfalls #4） |
| QA 报卡片子元素越界 | 减小内边距/字号，或在固定框内用 flex/grid 匀开 |
| `deck_audit` 报 PPTX 未同步 | 忘了重跑 `shot.py` 3x 或重新组包；补齐后重跑 |
| 3x 图尺寸不是 3840×2160 | `shot.py` 第三个参数必须传 `3` |
| 渲染出来字体不对 | 系统缺「微软雅黑」，安装字体后重启终端 |

---

## 8. 升级与卸载

- **升级**：重新运行 `python install.py`（会自动把旧版本备份为 `.bak-时间戳`），重启会话即可；
- **卸载**：删除 `~/.claude/skills/sgcc-report-ppt`（项目级则删项目下的对应目录）。

---

## 9. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.2 | 2026-11-06 | 技能发布到 GitHub；新增 `npx skills add AnTi-anti/ft-ppt-agent-skills` 安装方式（实测可发现技能） |
| v1.1 | 2026-11-05 | 新增 `deck_audit.py`、`delete_slide.py`、`patch_png_text.py`；`visual_qa.py` 增加导语条留白检查；`pitfalls.md` 扩至 17 条；`workflow.md` 增加改稿章节；移除旧 `visual_qa_local.py` |
| v1.0 | 2026-10 | 首版：风格合同、布局 A/B、渲染/QA/组包流水线、三张样例页 |
