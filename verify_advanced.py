import os
import duckdb

DATA = r"E:\codespace\ghub-projects\DuckDB-explore\data"
EMP = os.path.join(DATA, "employees.parquet").replace("\\", "/")
EVT = os.path.join(DATA, "events.json").replace("\\", "/")

con = duckdb.connect()

# 1. 递归 CTE：从员工D(10)往上找所有上级
print("=== 递归 CTE ===")
try:
    con.execute(f"CREATE TABLE employees AS SELECT * FROM read_parquet('{EMP}')")
    df = con.execute("""
        WITH RECURSIVE chain(id, name, manager_id, depth) AS (
            SELECT id, name, manager_id, 0 FROM employees WHERE id = 10
            UNION ALL
            SELECT e.id, e.name, e.manager_id, c.depth + 1
            FROM employees e JOIN chain c ON e.id = c.manager_id
        )
        SELECT id, name, depth FROM chain ORDER BY depth
    """).fetchdf()
    print(df.to_string())
except Exception as e:
    print("递归CTE ERR:", e)

# 2. ASOF JOIN
print("\n=== ASOF JOIN ===")
try:
    con.execute("""
        CREATE TABLE quotes (symbol VARCHAR, quote_time TIMESTAMP, price DECIMAL(10,2));
        CREATE TABLE trades (trade_time TIMESTAMP, symbol VARCHAR, qty INTEGER);
        INSERT INTO quotes VALUES ('AAPL','2024-01-01 09:00:00',180.00),('AAPL','2024-01-01 09:05:00',181.50),('AAPL','2024-01-01 09:10:00',182.00),('GOOG','2024-01-01 09:00:00',140.00),('GOOG','2024-01-01 09:06:00',141.00);
        INSERT INTO trades VALUES ('2024-01-01 09:03:00','AAPL',100),('2024-01-01 09:08:00','AAPL',50),('2024-01-01 09:04:00','GOOG',30);
    """)
    df = con.execute("""
        SELECT t.trade_time, t.symbol, t.qty, q.quote_time, q.price
        FROM trades t
        ASOF JOIN quotes q ON t.symbol = q.symbol AND t.trade_time >= q.quote_time
    """).fetchdf()
    print(df.to_string())
except Exception as e:
    print("ASOF ERR:", e)

# 3. JSON 查询
print("\n=== JSON 查询 ===")
try:
    df = con.execute(f"SELECT event_id, json_extract_string(user, '$.name') AS name, json_extract_string(user, '$.vip') AS vip FROM read_json_auto('{EVT}')").fetchdf()
    print(df.to_string())
except Exception as e:
    print("JSON ERR:", e)
