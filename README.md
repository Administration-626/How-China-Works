# How China Works

《置身事内》与《以日为鉴》两本书的阅读图谱。四张单文件 HTML 页面，样式、文本、插图全部内联，用浏览器直接打开，不需要本地服务，也不需要联网。

## 页面

| 文件 | 内容 |
|---|---|
| `index.html` | 《置身事内：中国政府与经济发展》（兰小欢）逐节图谱。章节卡、原书插图、概念与数据表，末尾第 20 节「K 型分化 · 已经形成」给出定义、五个断面与中美对照 |
| `riji.html` | 《以日为鉴：衰退时代生存指南》（分析师Boden）精讲。失业潮、学历贬值、医疗体系、全民出海，附日本 1989 至 2024 年的因果链 |
| `compare.html` | 两本书的对照。写作立场的差异、同一话题的两种写法、日本三十年与中国三十年 |
| `policy.html` | 农业改革政策备忘录。2026 年 10 月时点上已实施的措施、有明确排期的措施、六次退潮的对照 |

## 构建 index.html

只有 `index.html` 由 `src/` 下的脚本生成，其余三张是手写单文件。

1. `build_figs.py` 从 EPUB 抽取各章正文与插图，插图按 860 和 320 两档宽度压成 WebP 后编码为 base64，连同图注写入 `src/book.json`。EPUB 路径写在脚本顶部的 `SRC` 常量。
2. `build.py` 读取 `book.json` 与 `template.html`，并入脚本内嵌的章节摘要，重写根目录的 `index.html`。
3. `verify.py` 用 Playwright 打开 `http://127.0.0.1:8791/index.html`，跑结构、几何、时序、引用四层断言，截图存入 `src/shots`。运行前在项目根目录起服务：`python -m http.server 8791`。

## 限制

- `build.py` 整份重写 `index.html`。手工追加的小节不在脚本里，例如第 20 节 K 型分化，重建后消失。改动前先确认这一段是否要迁进 `build.py`。
- `build_figs.py` 的 `SRC` 与 `verify.py` 的 `CHROME` 是写死的绝对路径，换机器要改。
- `verify.py` 依赖 playwright 包与本地 Chromium，其余页面无依赖。
