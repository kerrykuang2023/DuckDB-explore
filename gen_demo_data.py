"""生成 DuckDB-explore 演示数据：导出不同压缩算法的 Parquet，用于展示文件格式/压缩对比。"""
import os
import duckdb

DATA = r"E:\codespace\ghub-projects\DuckDB-explore\data"
os.makedirs(DATA, exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL sqlite; LOAD sqlite;")
con.execute(f"ATTACH '{os.path.join(DATA, 'Walmart_Sales.db')}' AS wlm (TYPE sqlite)")

# 导出不同压缩算法的 Parquet，对比大小
compressions = ["SNAPPY", "GZIP", "ZSTD"]
print("=== Parquet 压缩对比（Walmart 6435 行）===")
for comp in compressions:
    path = os.path.join(DATA, f"sales_{comp.lower()}.parquet")
    con.execute(f"""
        COPY (SELECT * FROM wlm.walmart_sales)
        TO '{path}' (FORMAT PARQUET, COMPRESSION '{comp}')
    """)
    size = os.path.getsize(path)
    print(f"  {comp:8s}: {size/1024:.1f} KB  -> {path}")

# 导出 edu_orders 为 parquet（用于零 ETL 直查）
con.execute(f"ATTACH '{os.path.join(DATA, 'edu_orders.db')}' AS edu (TYPE sqlite)")
con.execute(f"""
    COPY (SELECT * FROM edu.orders)
    TO '{os.path.join(DATA, 'orders.parquet')}' (FORMAT PARQUET, COMPRESSION 'ZSTD')
""")
print(f"  orders.parquet: {os.path.getsize(os.path.join(DATA,'orders.parquet'))/1024:.1f} KB")

# 对比原始 SQLite 大小
print("\n=== 原始文件大小对比 ===")
for f in ["Walmart_Sales.db", "edu_orders.db", "courses_dim.csv"]:
    p = os.path.join(DATA, f)
    print(f"  {f}: {os.path.getsize(p)/1024:.1f} KB")
