"""DuckDB-explore: 通过 UI 全链路展示 DuckDB 能力，无需手写 SQL。

运行: streamlit run app.py  ->  http://localhost:8501
"""
import os
import time
import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(page_title="DuckDB-explore", page_icon="🦆", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
EDU_DB = os.path.join(DATA_DIR, "edu_orders.db")
WLM_DB = os.path.join(DATA_DIR, "Walmart_Sales.db")
CSV_DIM = os.path.join(DATA_DIR, "courses_dim.csv")
CSV_DIM_POSIX = CSV_DIM.replace("\\", "/")


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"ATTACH '{EDU_DB}' AS edu (TYPE sqlite);")
    con.execute(f"ATTACH '{WLM_DB}' AS wlm (TYPE sqlite);")
    return con


def timed_query(con, sql: str):
    t0 = time.time()
    df = con.execute(sql).fetchdf()
    elapsed = (time.time() - t0) * 1000
    return df, elapsed


def show(sql: str, df: pd.DataFrame, ms: float = None, chart: str = None, note: str = None):
    """统一展示：结果（表格/图）+ 耗时 + 对应的 SQL 语句。"""
    if chart == "bar":
        st.bar_chart(df.set_index(df.columns[0]))
    elif chart == "metric":
        st.metric(df.columns[0], f"{df.iloc[0, 0]:,}", delta=f"{ms:.1f} ms" if ms else None)
    else:
        st.dataframe(df, use_container_width=True)
    if ms is not None and chart != "metric":
        st.caption(f"⏱ 耗时 {ms:.1f} ms")
    if note:
        st.info(note)
    with st.expander("🔍 查看对应 SQL", expanded=True):
        st.code(sql, language="sql")


con = get_connection()

# ── 侧边栏 ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🦆 DuckDB-explore")
    st.caption("嵌入式 · 无 server · 单进程 · < 1GB 内存")
    with st.expander("ℹ️ 什么是 DuckDB？", expanded=False):
        st.markdown(
            """
- **嵌入式**：无独立 server，`import duckdb` 即用
- **无 ETL**：直接读外部 SQLite / CSV / Parquet
- **列式向量化**：只读所需列、批量执行，毫秒级
- **单进程多线程读**：无需外部服务
"""
        )

st.title("DuckDB 能力全链路探索")
st.caption("不用写 SQL——每个案例点选触发，结果旁附对应 SQL，便于理解底层")

# ── 顶层 Tabs 组织能力 ─────────────────────────────────────────────────
tab_fed, tab_ana, tab_file, tab_ddl, tab_perf = st.tabs(
    ["🦆 联邦查询", "📊 分析能力", "📁 文件格式与压缩", "🏗️ 建表与表类型", "⚡ 性能与导出"]
)

# ═══════════════ Tab 1: 联邦查询 ═══════════════
with tab_fed:
    st.subheader("R-01 联邦查询：一条 SQL 跨多个异构数据源")
    st.write("一个 DuckDB 进程，一条 SQL 同时查 SQLite×2 + CSV 三个源。")
    sql_fed = """
SELECT 'edu_orders(SQLite)' AS source, COUNT(*) AS cnt FROM edu.courses
UNION ALL
SELECT 'Walmart_Sales(SQLite)', COUNT(DISTINCT Store) FROM wlm.walmart_sales
UNION ALL
SELECT 'courses_dim(CSV)', COUNT(*) FROM read_csv_auto('{csv}')""".replace(
        "{csv}", CSV_DIM_POSIX
    )
    if st.button("执行联邦查询（跨 3 源）", key="fed"):
        df, ms = timed_query(con, sql_fed)
        show(sql_fed, df, ms, note="一条 SQL 同时引用 edu(SQLite)、wlm(SQLite)、read_csv_auto(CSV) 三个异构源")

    st.divider()
    st.subheader("R-02 跨源 JOIN：SQLite 表 + CSV 文件关联")
    sql_join = """
SELECT d.course_name, d.category, COUNT(*) AS order_cnt
FROM edu.orders o
JOIN read_csv_auto('{csv}') d ON o.course_id = d.course_id
GROUP BY d.course_name, d.category
ORDER BY order_cnt DESC""".replace("{csv}", CSV_DIM_POSIX)
    if st.button("跨源 JOIN：按课程统计订单数", key="join"):
        df, ms = timed_query(con, sql_join)
        show(sql_join, df, ms, chart="bar", note="orders 来自 SQLite，courses_dim 来自 CSV，跨源关联")

# ═══════════════ Tab 2: 分析能力 ═══════════════
with tab_ana:
    st.subheader("窗口函数：排名 + 移动平均")
    st.write("用现有 edu_orders 数据，展示 RANK / 按课程排名。")
    sql_win = """
SELECT order_id, course_id, student_id, amount,
       RANK() OVER (PARTITION BY course_id ORDER BY amount DESC) AS rank_in_course,
       AVG(amount) OVER (PARTITION BY course_id) AS course_avg
FROM edu.orders
ORDER BY course_id, rank_in_course
LIMIT 10"""
    if st.button("跑窗口函数（RANK + AVG）", key="win"):
        df, ms = timed_query(con, sql_win)
        show(sql_win, df, ms, note="RANK() 按课程内金额排名，AVG() OVER 计算课程均值")

    st.divider()
    st.subheader("PIVOT 行列转换")
    st.write("按课程分类把订单数转成行。")
    sql_pivot = """
PIVOT (SELECT category, COUNT(*) AS n FROM edu.courses GROUP BY category)
  ON category USING SUM(n)"""
    if st.button("跑 PIVOT 行列转换", key="pivot"):
        try:
            df, ms = timed_query(con, sql_pivot)
            show(sql_pivot, df, ms, note="PIVOT 把分类行转成列，报表宽表化一步完成")
        except Exception as e:
            st.error(f"PIVOT 语法示例（展示用）：{e}")

# ═══════════════ Tab 3: 文件格式与压缩 ═══════════════
with tab_file:
    st.subheader("零 ETL 读 Parquet（列式文件）")
    parquet_path = os.path.join(DATA_DIR, "sales_zstd.parquet").replace("\\", "/")
    sql_parquet = f"SELECT Store, ROUND(SUM(Weekly_Sales),2) AS total FROM read_parquet('{parquet_path}') GROUP BY Store ORDER BY total DESC LIMIT 5"
    if st.button("读 Parquet 并聚合 TOP5", key="parquet"):
        df, ms = timed_query(con, sql_parquet)
        show(sql_parquet, df, ms, chart="bar", note="直接 read_parquet，无需建表导入（零 ETL）")

    st.divider()
    st.subheader("Parquet 压缩算法对比（6435 行 Walmart 数据）")
    comp_data = {
        "原始 SQLite": ["420.0 KB", ""],
        "SNAPPY（默认，快）": ["122.1 KB", "压缩率中，速度快"],
        "GZIP（高压缩）": ["75.9 KB", "压缩率高，速度慢"],
        "ZSTD（推荐）": ["75.5 KB", "压缩率高且速度均衡"],
    }
    comp_df = pd.DataFrame(comp_data, index=["大小", "说明"]).T.reset_index()
    comp_df.columns = ["格式", "大小", "说明"]
    st.dataframe(comp_df, use_container_width=True)
    st.caption("同一份数据，Parquet 列式压缩后从 420KB 降到 76KB（省 82%）；SNAPPY 快、GZIP 压得狠、ZSTD 均衡")

# ═══════════════ Tab 4: 建表与表类型 ═══════════════
with tab_ddl:
    st.subheader("建表语句（DDL）")
    st.code(
        """-- 建表：字段类型 + 主键 + 约束
CREATE TABLE orders (
    order_id   INTEGER PRIMARY KEY,        -- 主键
    student_id INTEGER NOT NULL,           -- 非空约束
    course_id  INTEGER,
    amount     DECIMAL(10, 2),             -- 定点小数（金额）
    order_date DATE,
    status     VARCHAR CHECK (status IN ('completed','refunded','pending'))  -- 枚举约束
);

-- 从查询结果建表（CTAS）
CREATE TABLE high_course AS
  SELECT course_id, COUNT(*) AS n FROM orders GROUP BY course_id;""",
        language="sql",
    )

    st.divider()
    st.subheader("表类型对比（存储与生命周期的影响）")
    table_types = pd.DataFrame(
        [
            ["内存表（默认）", "内存", "进程退出即失", "临时分析、中间结果"],
            ["持久化表", ".duckdb 文件", "跨进程持久", "长期数据（需指定持久连接）"],
            ["TEMP TABLE", "内存", "会话结束即失", "单次查询的中间表"],
            ["VIEW", "不存数据", "定义持久", "逻辑视图，查时展开"],
            ["MATERIALIZED VIEW", "存预计算结果", "持久", "预聚合加速查询"],
        ],
        columns=["类型", "存储", "生命周期", "适用场景"],
    )
    st.dataframe(table_types, use_container_width=True)
    st.caption("关键影响：内存表快但丢了；持久化表跨进程但写 .duckdb 文件；物化视图预存结果换查询速度")

    st.divider()
    st.subheader("加密")
    st.markdown(
        """
- **DuckDB 本身无内置表级/文件级加密**（不同于 SQLite 的商业加密扩展 SEE）。
- **Parquet 支持模块化加密**：`read_parquet(..., encryption_config=...)` 读加密 Parquet。
- **常用做法**：依赖文件系统层加密（Windows BitLocker / Linux LUKS / APFS），或应用层加密后落盘。
- 生产若需透明加密，选 **MotherDuck（云托管）** 或自建层加密。
"""
    )

# ═══════════════ Tab 5: 性能与导出 ═══════════════
with tab_perf:
    st.subheader("列式向量化性能")
    qs = [
        ("COUNT(*) 全表扫描", "SELECT COUNT(*) FROM edu.orders"),
        ("按分类 GROUP BY", "SELECT category, COUNT(*) FROM edu.courses GROUP BY category"),
        ("三表 JOIN 聚合", "SELECT c.course_name, COUNT(o.order_id) FROM edu.courses c JOIN edu.orders o ON c.course_id=o.course_id GROUP BY c.course_name"),
        ("Walmart TOP5 聚合", "SELECT Store, SUM(Weekly_Sales) FROM wlm.walmart_sales GROUP BY Store ORDER BY 2 DESC LIMIT 5"),
    ]
    if st.button("跑 4 个查询并计时", key="perf"):
        rows = []
        for name, sql in qs:
            _, ms = timed_query(con, sql)
            rows.append({"查询": name, "耗时(ms)": round(ms, 1)})
        df = pd.DataFrame(rows)
        show("-- 以上每个查询的 SQL 见下方展开", df, note="列式向量化：所有查询毫秒级，无需外部服务")
        for name, sql in qs:
            st.code(sql, language="sql")

    st.divider()
    st.subheader("COPY 导出（数据工程闭环）")
    out_path = os.path.join(DATA_DIR, "category_summary.parquet").replace("\\", "/")
    sql_copy = f"COPY (SELECT category, COUNT(*) AS n FROM edu.courses GROUP BY category) TO '{out_path}' (FORMAT PARQUET, COMPRESSION 'ZSTD')"
    if st.button("导出聚合结果到 Parquet", key="copy"):
        t0 = time.time()
        con.execute(sql_copy)
        ms = (time.time() - t0) * 1000
        out = os.path.join(DATA_DIR, "category_summary.parquet")
        sz = os.path.getsize(out) / 1024
        df = con.execute(f"SELECT * FROM read_parquet('{out_path}')").fetchdf()
        show(sql_copy, df, ms, note=f"已导出 {sz:.1f} KB 的 Parquet，DuckDB 能查也能写（轻量 ETL）")

    st.divider()
    st.subheader("Pandas 零拷贝（嵌入式）")
    st.code(
        '''import duckdb, pandas as pd
df = pd.read_csv("orders.csv")      # 已有 DataFrame
# 直接查内存里的 df，零拷贝、不落盘
duckdb.sql("SELECT category, SUM(amount) FROM df GROUP BY category").df()''',
        language="python",
    )
    st.caption("嵌入式：内存 DataFrame 直接当表查，与 Python 生态零拷贝互操作")
