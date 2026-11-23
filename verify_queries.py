import os
import time
import duckdb

DATA = r"E:\codespace\ghub-projects\DuckDB-explore\data"
EDU = os.path.join(DATA, "edu_orders.db")
WLM = os.path.join(DATA, "Walmart_Sales.db")
CSV = os.path.join(DATA, "courses_dim.csv").replace("\\", "/")

con = duckdb.connect()
con.execute("INSTALL sqlite; LOAD sqlite;")
con.execute(f"ATTACH '{EDU}' AS edu (TYPE sqlite)")
con.execute(f"ATTACH '{WLM}' AS wlm (TYPE sqlite)")

print("=== 跨源 JOIN (SQLite orders + CSV courses_dim) ===")
t0 = time.time()
df = con.execute(
    f"SELECT d.course_name, d.category, COUNT(*) AS order_cnt FROM edu.orders o JOIN read_csv_auto('{CSV}') d ON o.course_id=d.course_id GROUP BY d.course_name, d.category ORDER BY order_cnt DESC"
).fetchdf()
print(f"耗时 {(time.time()-t0)*1000:.1f}ms, 行数 {len(df)}")
print(df.head(3).to_string())

print("\n=== Walmart TOP5 ===")
t0 = time.time()
df = con.execute(
    "SELECT Store, ROUND(SUM(Weekly_Sales),2) AS total FROM wlm.walmart_sales GROUP BY Store ORDER BY total DESC LIMIT 5"
).fetchdf()
print(f"耗时 {(time.time()-t0)*1000:.1f}ms")
print(df.to_string())

print("\n=== 节假日 vs 非节假日 ===")
df = con.execute(
    "SELECT Holiday_Flag, ROUND(AVG(Weekly_Sales),2) AS avg_sales FROM wlm.walmart_sales GROUP BY Holiday_Flag"
).fetchdf()
print(df.to_string())
