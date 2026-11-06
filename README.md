# sgcc-report-ppt（Agent Skill）

国网 / 电网系统正式汇报 PPT 的**风格层 + 交付流水线**：统一「编号+判断句」标题、左图卡+右栏布局、正式书面口吻，配套 HTML → PNG → PPTX 的渲染、QA、组包脚本。

## 安装

### 方式一：Agent Skills CLI（推荐，跨客户端）

```bash
npx skills add AnTi-anti/ft-ppt-agent-skills
```

CLI 会自动识别 `skills/sgcc-report-ppt/SKILL.md` 并安装到当前 AI 客户端的技能目录。

常用参数：

```bash
npx skills add AnTi-anti/ft-ppt-agent-skills -l      # 先预览仓库里有哪些技能
npx skills add AnTi-anti/ft-ppt-agent-skills -g -y   # 装到用户级目录，跳过确认
npx skills add AnTi-anti/ft-ppt-agent-skills --copy  # 复制文件而非软链接
```

安装后新开一次会话，输入 `/` 应能看到 `sgcc-report-ppt`。

### 方式二：手动安装

把 `skills/sgcc-report-ppt` 复制到客户端的技能目录，例如：

- Claude Code：`~/.claude/skills/sgcc-report-ppt`
- 项目内：`<项目>/.claude/skills/sgcc-report-ppt`

### 环境依赖

```bash
python -m pip install playwright python-pptx pillow
python -m playwright install chromium
```

## 客户端兼容性

| 客户端 | 安装方式 | 说明 |
|---|---|---|
| Claude Code | `npx skills add` / 手动复制 | 完整支持技能自动加载与斜杠命令 |
| 支持 Agent Skills 的其他客户端 | `npx skills add` | 取决于客户端是否实现 SKILL.md 规范 |
| 仅支持规则文件（AGENTS.md / rules）的客户端 | 手动 | 把 SKILL.md 作为规则/指令喂入，脚本照常调用 |
| 任意环境（含内网离线） | 离线包 | 用 `install.py` 或直接复制文件夹 |

> 脚本本身是纯 Python，不依赖任何特定 AI 客户端；差异只在「是否自动发现技能」。

## 目录

```
skills/sgcc-report-ppt/
├── SKILL.md
├── references/    # 布局、口吻、CSS、坑与修法、流水线、安装说明
├── scripts/       # 渲染、QA、整册核对、组包、删页、图内改字
└── assets/example # 三张成品样例页
```
