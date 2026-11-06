# 可复用 CSS 片段（国网汇报风格）

> 每页 HTML 自带 `<style>`；以下片段直接粘贴使用。所有坐标基于 1280×720 画布，内容区 232–666。

## 1. 全局变量（每页 :root 固定）

```css
:root{
  --card-border:#D7DCDA; --card-radius:4px;
  --text-primary:#1B2A2C; --text-secondary:#59696C; --text-tertiary:#66777A;
  --accent-1:#009C9A; --accent-2:#FF9700;
  --teal-text:#00726F; --orange-text:#B36A00;
  --hairline:#D7DCDA; --hairline-soft:#E6EBE9;
  --bg-secondary:#EFF8F8; --surface-muted:#E6EBE9;
  --shadow-card:0 1px 2px rgba(0,60,58,0.04);
  --tpl-title:#00B2B0; --tpl-rule:#00C0C1; --tpl-frame:#CCF2F2;
  --font-primary:"Microsoft YaHei","微软雅黑","DengXian","等线",sans-serif;
}
*{box-sizing:border-box;}
html,body{margin:0;padding:0;}
body{width:1280px;height:720px;overflow:hidden;background:#FFF;
     font-family:var(--font-primary);color:var(--text-primary);
     -webkit-font-smoothing:antialiased;}
.slide{position:relative;width:1280px;height:720px;overflow:hidden;background:#FFF;}
```

## 2. 图卡（左卡）

```css
.fig-card{position:absolute;left:39px;top:232px;width:661px;height:434px;
  display:flex;flex-direction:column;
  background:#FFF;border:1px solid var(--card-border);border-radius:4px;
  box-shadow:var(--shadow-card);padding:11px 14px 10px;z-index:3;}
.fig-head{display:flex;justify-content:space-between;align-items:baseline;flex:0 0 auto;}
.fig-head h2{margin:0;font-size:15px;font-weight:600;color:var(--text-primary);}
.fig-head span{font-size:12px;color:var(--text-tertiary);}
.fig-body{flex:1 1 auto;min-height:0;display:flex;align-items:center;justify-content:center;margin-top:6px;}
.fig-body img{display:block;height:100%;width:auto;max-width:100%;object-fit:contain;}
```

> 图与框比例不一致时用 `height:100%;width:auto;object-fit:contain`，或先用 Pillow 裁剪图片到接近框比例（见 pitfalls #3）。

## 3. KPI 行（五格）

```css
.kpi{display:grid;grid-template-columns:repeat(5,1fr);margin-top:12px;
     padding-bottom:12px;border-bottom:1px solid var(--hairline-soft);}
.kpi .k{display:flex;flex-direction:column;gap:1px;}
.kpi b{font-size:31px;line-height:1.05;font-weight:700;color:var(--text-primary);
       font-variant-numeric:tabular-nums;}
.kpi b small{font-size:13px;font-weight:600;color:var(--text-secondary);margin-left:2px;}
.kpi span{font-size:12.5px;line-height:1.3;color:var(--text-primary);}
.kpi em{font-style:normal;font-size:12px;line-height:1.35;color:var(--text-tertiary);}
```

## 4. 横向条形对比（两段式）

```css
.brow{display:flex;align-items:center;gap:14px;}
.brow .bl{flex:0 0 148px;display:flex;flex-direction:column;gap:2px;}
.brow .bl span{font-size:13px;font-weight:600;color:var(--text-primary);}
.brow .bl em{font-style:normal;font-size:12px;color:var(--text-tertiary);}
.brow .bar{flex:1 1 auto;display:flex;height:34px;border:1px solid var(--card-border);
           border-radius:3px;overflow:hidden;background:#FFF;}
.brow .seg{display:flex;align-items:center;gap:6px;padding-left:8px;white-space:nowrap;}
.brow .seg.teal{background:#009C9A;color:#FFF;}
.brow .seg.white{background:#F2F6F5;color:var(--text-primary);border-left:1px solid var(--card-border);}
.brow .seg.orange{background:#F0A24B;color:#FFF;}
```

## 5. 步骤网格（3×2 / 6 步流程）

```css
.steps{flex:1 1 auto;min-height:0;display:grid;
       grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;
       gap:10px 12px;margin-top:14px;}
.st{position:relative;background:#FAFCFB;border:1px solid var(--card-border);
    border-radius:4px;padding:10px 12px 8px;}
.st .n{position:absolute;right:10px;top:9px;font-size:12px;font-weight:700;
       color:var(--text-tertiary);font-variant-numeric:tabular-nums;}
.st h3{margin:0;font-size:14px;line-height:1.3;font-weight:600;color:var(--text-primary);}
.st p{margin:5px 0 0;font-size:12px;line-height:1.45;color:var(--text-secondary);}
.st.orange-top{border-top:3px solid #C55A11;}   /* 问题段 */
.st.green-top {border-top:3px solid #548235;}   /* 方案段 */
```

## 6. 右栏卡片（结论 / 口径 / 后续）

```css
.rail-card{position:absolute;left:716px;width:525px;background:#FFF;
  border:1px solid var(--card-border);border-radius:4px;box-shadow:var(--shadow-card);
  padding:10px 16px;z-index:3;}
.rail-card .kick{display:block;font-size:12px;font-weight:700;
  letter-spacing:1.8px;color:var(--text-tertiary);}
.rail-card h2{margin:6px 0 0;font-size:18px;font-weight:600;color:var(--text-primary);}
.rail-card p{margin:6px 0 0;font-size:12.5px;line-height:1.5;color:var(--text-secondary);}
```

## 7. 口径/限定说明条

```css
.note{margin:7px 0 0;font-size:12px;line-height:1.3;color:var(--text-tertiary);}
.note b{color:var(--text-secondary);}
```

## 8. 表格（对比表）

```css
.tbl{width:100%;border-collapse:collapse;font-size:12.5px;
     font-variant-numeric:tabular-nums;}
.tbl th{font-size:12px;font-weight:600;color:var(--text-tertiary);
        text-align:left;padding:4px 8px;border-bottom:1px solid var(--card-border);}
.tbl td{padding:6px 8px;border-bottom:1px solid var(--hairline-soft);color:var(--text-primary);}
.tbl td.num{text-align:right;}
```

## 使用注意

- **类名必须带页面前缀**（`.p17-kpi`、`.p20-cols`），严禁用 `.k`、`.bk`、`.lg` 这类全局短类名——旧页 CSS 常残留同名绝对定位规则，会把新结构压到左上角（见 pitfalls #1）。
- 所有卡片加 `data-card-id`，QA 会检查子元素是否越界。
