# ADR-001：UI 技术选型 — Streamlit

## 状态
已接受（Accepted）

## 背景
DuckDB-explore 需要一个 UI 来"全链路清晰展示 DuckDB 的各种特性，而不是用 SQL"。需要快速、纯 Python、与 DuckDB 生态契合、且便于 ATDD 验证的方案。

## 决策
采用 **Streamlit** 作为 UI 框架。

## 理由
1. **纯 Python**：与 DuckDB（Python 嵌入式）同语言，`import duckdb` + `import streamlit` 直接集成，无跨语言胶水。
2. **DuckDB 官方生态契合**：DuckDB 官方文档大量使用 Streamlit 做演示，社区示例丰富，最佳实践成熟。
3. **快速迭代**：Streamlit 脚本式开发，改代码即时刷新，适合 ATDD 的 RED/GREEN 快速验证循环。
4. **可视化内建**：`st.dataframe` / `st.bar_chart` / `st.metric` 等原生组件，满足"展示特性"需求，无需手写前端图表。
5. **验证成本低**：`verify-acceptance` 用 `streamlit run app.py` 一条命令启动，`http://localhost:8501` 可直接验收。

## 备选方案
| 方案 | 弃用原因 |
|---|---|
| Gradio | 偏模型演示，数据分析表格/指标展示不如 Streamlit |
| FastAPI + 前端框架 | 引入前端构建链，迭代慢，违背"快速验证"目标 |
| Panel/HoloViz | 交互性强但学习曲线高，生态示例不如 Streamlit 多 |

## 影响
- 项目依赖：`streamlit` + `duckdb`（记录在 requirements.lock）
- 入口：`app.py`，`streamlit run app.py` 启动，默认 8501 端口
- ATDD verify 阶段用 loopback URL `http://localhost:8501`

## 数据源
演示数据从 `data/` 目录复制到项目内（自包含），避免依赖外部绝对路径。
