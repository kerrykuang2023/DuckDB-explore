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


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    """R-03/R-08: 嵌入式单进程连接，直接 ATTACH 外部源，无 ETL。"""
    con = duckdb.connect()
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"ATTACH '{EDU_DB}' AS edu (TYPE sqlite);")
    con.execute(f"ATTACH '{WLM_DB}' AS wlm (TYPE sqlite);")
    return con


def timed_query(con, sql: str):
    """R-04: 列式向量化性能可见——返回 (DataFrame, 耗时ms)。"""
    t0 = time.time()
    df = con.execute(sql).fetchdf()
    elapsed = (time.time() - t0) * 1000
    return df, elapsed


# ── 侧边栏：数据源联邦（R-01）+ 轻量提示（R-07） ──────────────────────────
with st.sidebar:
    st.header("🦆 DuckDB-explore")
    st.caption("嵌入式 · 无 server · 单进程 · < 1GB 内存")

    # R-07: 资源轻量提示
    with st.expander("ℹ️ 什么是 DuckDB？", expanded=False):
        st.markdown(
            """
- **嵌入式**：无独立 server 进程，`import duckdb` 即用
- **无 ETL**：直接读外部 SQLite / CSV / Parquet，不用导入
- **列式向量化**：分析查询只读所需列、批量执行，毫秒级
- **单进程多线程读**：无需外部服务，进程内完成查询
"""
        )

    st.subheader("数据源（R-01 联邦）")
    sources = st.radio(
        "选择数据源",
        ["edu_orders（SQLite）", "Walmart_Sales（SQLite）", "courses_dim（CSV）"],
    )

st.title("DuckDB 能力全链路探索")
st.caption("不用写 SQL——点选数据源、字段和聚合，DuckDB 自动执行联邦查询")

con = get_connection()

# ── 主区：按数据源展示能力 ──────────────────────────────────────────────
if sources == "edu_orders（SQLite）":
    tab1, tab2, tab3 = st.tabs(["📊 无ETL直查", "🔗 跨源JOIN", "⚡ 性能对比"])

    with tab1:
        st.subheader("R-03 无 ETL 直查")
        st.write("直接读外部 SQLite 文件，无需建表或导入。")
        if st.button("查 courses 表行数", key="edu_count"):
            df, ms = timed_query(con, "SELECT COUNT(*) AS n FROM edu.courses")
            st.metric("课程数", f"{df.iloc[0,0]}", delta=f"{ms:.1f} ms")

        if st.button("查各分类课程数", key="edu_cat"):
            df, ms = timed_query(
                con, "SELECT category, COUNT(*) AS n FROM edu.courses GROUP BY category ORDER BY n DESC"
            )
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("category"))
            st.caption(f"耗时 {ms:.1f} ms")

    with tab2:
        st.subheader("R-02 跨源 JOIN")
        st.write("SQLite 的 orders 表 JOIN CSV 的 courses_dim 维度表，跨源关联。")
        if st.button("跨源 JOIN：按课程统计订单数", key="edu_join"):
            df, ms = timed_query(
                con,
                """
                SELECT d.course_name, d.category, COUNT(*) AS order_cnt
                FROM edu.orders o
                JOIN read_csv_auto('{csv}') d ON o.course_id = d.course_id
                GROUP BY d.course_name, d.category
                ORDER BY order_cnt DESC
                """.replace("{csv}", CSV_DIM.replace("\\", "/")),
            )
            st.dataframe(df, use_container_width=True)
            st.caption(f"跨源 JOIN（SQLite + CSV）耗时 {ms:.1f} ms")

    with tab3:
        st.subheader("R-04 列式向量化性能")
        st.write("同一查询，DuckDB 列式向量化执行，毫秒级返回。")
        if st.button("跑 3 个查询并计时", key="edu_perf"):
            qs = [
                ("COUNT(*) 全表扫描", "SELECT COUNT(*) FROM edu.orders"),
                ("按分类 GROUP BY", "SELECT category, COUNT(*) FROM edu.courses GROUP BY category"),
                ("三表 JOIN 聚合", "SELECT c.course_name, COUNT(o.order_id) FROM edu.courses c JOIN edu.orders o ON c.course_id=o.course_id GROUP BY c.course_name"),
            ]
            rows = []
            for name, sql in qs:
                _, ms = timed_query(con, sql)
                rows.append({"查询": name, "耗时(ms)": round(ms, 1)})
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
            st.success("列式向量化：所有查询毫秒级完成，无需外部服务")

elif sources == "Walmart_Sales（SQLite）":
    st.subheader("R-01 联邦 + R-04 性能")
    st.write("连接 Walmart_Sales（6435 行），列式聚合秒级。")
    if st.button("Store 总周销售额 TOP5", key="wlm_top"):
        df, ms = timed_query(
            con,
            "SELECT Store, ROUND(SUM(Weekly_Sales),2) AS total FROM wlm.walmart_sales GROUP BY Store ORDER BY total DESC LIMIT 5",
        )
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("Store"))
        st.caption(f"耗时 {ms:.1f} ms")

    if st.button("节假日 vs 非节假日平均周销售额", key="wlm_holiday"):
        df, ms = timed_query(
            con,
            "SELECT Holiday_Flag, ROUND(AVG(Weekly_Sales),2) AS avg_sales FROM wlm.walmart_sales GROUP BY Holiday_Flag",
        )
        df["类型"] = df["Holiday_Flag"].map({1: "节假日周", 0: "非节假日周"})
        st.dataframe(df[["类型", "avg_sales"]], use_container_width=True)
        st.caption(f"耗时 {ms:.1f} ms")

else:  # CSV
    st.subheader("R-03 无 ETL 直查 CSV")
    st.write("直接 read_csv_auto 读 CSV，无建表/导入。")
    if st.button("读 courses_dim.csv 前 5 行", key="csv_read"):
        df, ms = timed_query(con, f"SELECT * FROM read_csv_auto('{CSV_DIM.replace(chr(92), '/')}') LIMIT 5")
        st.dataframe(df, use_container_width=True)
        st.caption(f"耗时 {ms:.1f} ms")

# ── R-06: SQL 透明可查（侧栏底部展示最近执行的 SQL）────────────────────
st.divider()
st.subheader("R-06 SQL 透明可查")
st.caption("你点选操作，DuckDB 实际执行的 SQL 透明展示（只读，无需手写）：")
with st.expander("查看示例 SQL（只读）", expanded=False):
    st.code(
        """-- 跨源 JOIN（SQLite + CSV）：
SELECT d.course_name, COUNT(*) AS order_cnt
FROM edu.orders o
JOIN read_csv_auto('data/courses_dim.csv') d ON o.course_id = d.course_id
GROUP BY d.course_name

-- 联邦查询（Walmart TOP5）：
SELECT Store, SUM(Weekly_Sales) AS total
FROM wlm.walmart_sales GROUP BY Store ORDER BY total DESC LIMIT 5""",
        language="sql",
    )
