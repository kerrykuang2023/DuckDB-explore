import os, duckdb
DATA = r"E:\codespace\ghub-projects\DuckDB-explore\data"
EDU = os.path.join(DATA, "edu_orders.db")
P = os.path.join(DATA, "sales_zstd.parquet").replace("\\", "/")
O = os.path.join(DATA, "category_summary.parquet").replace("\\", "/")
con = duckdb.connect()
con.execute("INSTALL sqlite; LOAD sqlite;")
con.execute(f"ATTACH '{EDU}' AS edu (TYPE sqlite)")
df = con.execute(f"SELECT Store, ROUND(SUM(Weekly_Sales),2) AS total FROM read_parquet('{P}') GROUP BY Store ORDER BY total DESC LIMIT 5").fetchdf()
print("read_parquet OK:", len(df), "行", df.iloc[0].to_dict())
con.execute(f"COPY (SELECT category, COUNT(*) AS n FROM edu.courses GROUP BY category) TO '{O}' (FORMAT PARQUET, COMPRESSION 'ZSTD')")
print("COPY OK:", os.path.getsize(O), "bytes")
