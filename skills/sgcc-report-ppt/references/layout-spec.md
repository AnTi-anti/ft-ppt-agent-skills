# 国网汇报 PPT 布局规范（1280×720 画布）

> 真源示例：`assets/example/slide-4-left-fig-right-rail.html`（左图卡+右栏）、`slide-8-wide-fig-narrow-rail.html`（宽图+窄栏）、`slide-3-section-toc.html`（子目录页）。

## 目录

1. 页面外壳（模板标题区）
2. 内容区网格（两种主布局）
3. 卡片通用样式
4. 页面类型与节奏
5. 密度要求

## 1. 页面外壳（模板标题区）

参考 PPT 的固定外壳，每页相同（坐标来自 slide-4，可直接复制其 CSS）：

| 元素 | 位置/尺寸 | 说明 |
|---|---|---|
| `.tpl-mark` 双叠方块 | left:37.8px top:20.5px, 54.6×54.6 | 外框线 1px `--tpl-rule` + 内部实心方块 ::after |
| `.slide-header` | left:110.8px top:24.7px, 宽1060 | 含 `.page-title` + `.hdr-meta` |
| `.page-title` | 字号 37.33px (28pt)、700、`--tpl-title` 青色、nowrap | **标题风格：「编号 + 主题」**，如「4.2 温度输入偏差直接拉低模型精度」，禁止口语句子式标题 |
| `.tpl-rule` 通栏细线 | left:88.2px top:78.7px, 1191.8×1.33px | 青色横线 |
| `.tpl-lede` 导语条 | left:38.9px top:95.2px, 1214×122 | 白底 + `--tpl-frame` 边框，字号 20px，重点用 `<b>`，警示用 `<em>`（#C00000） |
| 内容区起点 | top:232px，左右 39px 起 | 导语条以下全部是内容区 |

页面右上角 `.hdr-meta`：两行小字（如「AI 赋能 · 负荷预测」「2025-10」），右对齐、letter-spacing 大。

## 2. 内容区网格（两种主布局）

内容区 y 范围 232–666（高 434），x 范围 39–1253。

### 布局 A：左图卡 + 右栏（参考第4页）
- **左图卡**：left:39px，width:661px，height:434px — 图表/主视觉/流程图
- **右栏**：left:716px，width:525px — 纵向堆 2–4 个卡片（如 结论卡 212px + 口径卡 112px + 后续卡 90px，间隔 ~12px）

### 布局 B：宽图 + 窄栏（参考第8页）
- **左图卡**：left:39px，width:927px，height:434px — 宽幅曲线图/对比图
- **右窄栏**：left:983px，width:270px — 纵向堆 3 个小块（大数字 delta 卡等）

选择规则：图占主导且信息在横向趋势上 → B；图+说明并列、右栏要放结论文字 → A。

## 3. 卡片通用样式

```css
background:#FFFFFF; border:1px solid var(--card-border); /* #D7DCDA */
border-radius:4px; box-shadow:var(--shadow-card);        /* 0 1px 2px rgba(0,60,58,.04) */
padding:10px 16px;                                        /* 左右 16，上下 10 */
```

卡内小节标题（`.pN-kick` 类）：12px / 700 / letter-spacing:1.6px / `--teal-text`。
大数字：26–31px / 700 / tabular-nums / 青绿或橙。
正文：12–12.5px，行高 1.4–1.55，`--text-secondary`。

## 4. 页面类型与节奏

| 页型 | 结构 | 备注 |
|---|---|---|
| 封面 | 大标题居中/左对齐 + 汇报人/日期 | 不放「内部技术汇报」类字样除非用户要求 |
| 主目录 | 3 个章节块 | — |
| 子目录页（每章前插一页） | 参考 slide-3 example | 章号 + 本章小节列表 |
| 内容页 | 布局 A 或 B | 导语条一句话点题 |
| 结尾页 | 致谢/总结 | — |

## 5. 密度要求（国网汇报特点：内容实、不留大空白）

- **框内不得有大块死空间**：卡片高度应贴合内容；若框已定，内容在框内匀开（flex/grid 撑满、`justify-content:space-between/space-around`、末段 `margin-top:auto` 压底）。
- 每页信息承载：≥3 个数据支撑点（KPI/对比/结论），纯文字段不超过 2 行/段。
- 全页墨水覆盖率（QA 指标）0.03–0.65 之间，接近 0.65 会 WARN "very busy"，国网页常偏高属正常。
