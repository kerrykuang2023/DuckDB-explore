import os, time, duckdb
DATA = r"E:\codespace\ghub-projects\DuckDB-explore\data"
EDU = os.path.join(DATA, "edu_orders.db")
WLM = os.path.join(DATA, "Walmart_Sales.db")
CSV = os.path.join(DATA, "courses_dim.csv").replace("\\", "/")
con = duckdb.connect()
con.execute("INSTALL sqlite; LOAD sqlite;")
con.execute(f"ATTACH '{EDU}' AS edu (TYPE sqlite)")
con.execute(f"ATTACH '{WLM}' AS wlm (TYPE sqlite)")
t0 = time.time()
df = con.execute(f"""
SELECT 'edu_orders(SQLite)' AS source, COUNT(*) AS cnt FROM edu.courses
UNION ALL
SELECT 'Walmart_Sales(SQLite)', COUNT(DISTINCT Store) FROM wlm.walmart_sales
UNION ALL
SELECT 'courses_dim(CSV)', COUNT(*) FROM read_csv_auto('{CSV}')
""").fetchdf()
print(f"联邦查询耗时 {(time.time()-t0)*1000:.1f}ms")
print(df.to_string())
