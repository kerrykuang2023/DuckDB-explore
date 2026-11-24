import os
import duckdb

DATA = r"E:\codespace\ghub-projects\DuckDB-explore\data"
EDU = os.path.join(DATA, "edu_orders.db")
WLM = os.path.join(DATA, "Walmart_Sales.db")
CSV = os.path.join(DATA, "courses_dim.csv").replace("\\", "/")

con = duckdb.connect()
con.execute("INSTALL sqlite; LOAD sqlite;")
con.execute(f"ATTACH '{EDU}' AS edu (TYPE sqlite)")
con.execute(f"ATTACH '{WLM}' AS wlm (TYPE sqlite)")

# 1. 窗口函数
try:
    df = con.execute("""
        SELECT order_id, course_id, amount,
               RANK() OVER (PARTITION BY course_id ORDER BY amount DESC) AS rank_in_course
        FROM edu.orders ORDER BY course_id, rank_in_course LIMIT 10
    """).fetchdf()
    print("窗口函数 OK:", len(df), "行")
except Exception as e:
    print("窗口函数 ERR:", e)

# 2. PIVOT
try:
    df = con.execute("PIVOT (SELECT category, COUNT(*) AS n FROM edu.courses GROUP BY category) ON category USING SUM(n)").fetchdf()
    print("PIVOT OK:", df.shape)
except Exception as e:
    print("PIVOT ERR:", repr(e)[:200])

# 3. read_parquet
try:
    df = con.execute("SELECT Store, ROUND(SUM(Weekly_Sales),2) AS total FROM read_parquet('data/sales_zstd.parquet') GROUP BY Store ORDER BY total DESC LIMIT 5").fetchdf()
    print("read_parquet OK:", len(df), "行")
except Exception as e:
    print("read_parquet ERR:", e)

# 4. COPY 导出
try:
    con.execute("COPY (SELECT category, COUNT(*) AS n FROM edu.courses GROUP BY category) TO 'data/category_summary.parquet' (FORMAT PARQUET, COMPRESSION 'ZSTD')")
    print("COPY OK:", os.path.getsize(os.path.join(DATA, "category_summary.parquet")), "bytes")
except Exception as e:
    print("COPY ERR:", e)

# 5. 联邦 UNION
try:
    df = con.execute(f"""
        SELECT 'edu' AS s, COUNT(*) FROM edu.courses
        UNION ALL SELECT 'wlm', COUNT(DISTINCT Store) FROM wlm.walmart_sales
        UNION ALL SELECT 'csv', COUNT(*) FROM read_csv_auto('{CSV}')
    """).fetchdf()
    print("联邦 UNION OK:", len(df), "行")
except Exception as e:
    print("联邦 UNION ERR:", e)
