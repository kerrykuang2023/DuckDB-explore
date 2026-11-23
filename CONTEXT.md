# DuckDB-explore 共享语言文件（CONTEXT）

本文档是全项目的共享语言基线，统一 DuckDB 能力探索 UI 的术语和口径。评审（review-architecture / review-intent）以本文为准则。

## 术语表

| 术语 | 定义 |
|---|---|
| **DuckDB** | 嵌入式 OLAP 数据库引擎，无 server，进程内运行，列式向量化执行 |
| **联邦查询** | 一个 DuckDB 进程连接多个异构数据源（SQLite / CSV / Parquet / PostgreSQL / MySQL），用统一 SQL 跨源查询 |
| **跨源 JOIN** | 两个不同来源（如 SQLite 表 + CSV 文件）在一条查询里按条件关联 |
| **列式存储** | 数据按列组织，分析查询只读取所需列，配合向量化执行 |
| **向量化执行** | 一批批处理同列数据（而非一行行），利用 CPU SIMD，大幅提升分析性能 |
| **无 ETL 直查** | 不导入数据，DuckDB 直接读外部文件/库 |
| **嵌入式（embedded）** | 无独立 server 进程，作为库嵌入应用，`import duckdb` 即用 |
| **ATTACH** | DuckDB 连接外部数据源的方式（`ATTACH 'x.db' AS alias (TYPE sqlite)`） |
| **数据源** | 本次探索 UI 支持的输入：SQLite 库、CSV 文件、Parquet 文件 |

## 核心能力清单（UI 要展示的 DuckDB 特性）

1. **联邦查询**：连接多个数据源，统一 SQL 查询
2. **跨源 JOIN**：跨 SQLite 表 + CSV/Parquet 文件做关联
3. **列式 + 向量化**：只读所需列、批量执行，性能快
4. **无 ETL**：直接查外部文件，不用建表导入
5. **资源轻量**：< 1GB 内存，无 server
6. **性能可观测**：查询耗时毫秒级可见

## 已准备的演示数据

| 数据源 | 路径 | 内容 |
|---|---|---|
| edu_orders.db（SQLite） | `E:\codespace\ghub-projects\dbgpt-run\edu_orders.db` | 在线教育：courses/students/orders/reviews |
| Walmart_Sales.db（SQLite） | `E:\codespace\ghub-projects\DB-GPT\pilot\examples\Walmart_Sales.db` | 沃尔玛销售：walmart_sales 表 |
| CSV 示例 | 项目内 `data/*.csv` | 维度表，用于演示跨源 JOIN |

## 非目标（Non-goals）

- 不实现分布式（DuckDB 单机嵌入式，这是它的定位）
- 不实现高并发写入（DuckDB 单 writer）
- 不替换生产 OLTP 数据库
- 不做成通用 BI 平台（只做 DuckDB 能力探索演示）
