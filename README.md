# DuckDB-explore

通过 Streamlit UI 全链路展示 DuckDB 能力，无需手写 SQL。

## 运行

```powershell
# 1. 建 venv 装依赖（首次）
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. 启动
.\.venv\Scripts\python.exe -m streamlit run app.py
```

打开 http://localhost:8501

## 展示的 DuckDB 特性

| 规则 | 特性 | UI 入口 |
|---|---|---|
| R-01 | 数据源联邦 | 侧边栏选数据源（SQLite × 2 + CSV） |
| R-02 | 跨源 JOIN | edu_orders 标签页"跨源JOIN"（SQLite+CSV） |
| R-03 | 无 ETL 直查 | 直接 ATTACH / read_csv_auto |
| R-04 | 列式向量化性能 | 每查询显示毫秒耗时 |
| R-05 | 结果可视化 | dataframe + bar_chart + metric |
| R-06 | SQL 透明可查 | 底部只读 SQL 展示 |
| R-07 | 资源轻量 | 侧边栏信息卡片 |
| R-08 | 单进程多线程读 | 全程嵌入式，无外部服务 |

## 数据

- `data/edu_orders.db`（SQLite）：在线教育 4 表
- `data/Walmart_Sales.db`（SQLite）：沃尔玛销售
- `data/courses_dim.csv`：课程维度表（跨源 JOIN 用）

## ATDD 产物

- `specs/duckdb-explore/context.md` — impact map（8 条业务规则）
- `specs/duckdb-explore/*.feature` — Gherkin 场景
- `specs/duckdb-explore/review.md` — spec 评审（VERDICT: OK）
- `CONTEXT.md` / `docs/adr/` — 共享语言 + ADR
