"""生成高级特性演示数据：递归 CTE（层级）、ASOF JOIN（时间序列）、JSON 查询。"""
import os
import json
import duckdb

DATA = r"E:\codespace\ghub-projects\DuckDB-explore\data"
os.makedirs(DATA, exist_ok=True)

con = duckdb.connect()

# 1. 员工层级表（递归 CTE）
con.execute("""
CREATE TABLE employees (id INTEGER, name VARCHAR, manager_id INTEGER);
INSERT INTO employees VALUES
  (1, '张总(CEO)', NULL),
  (2, '李VP(技术)', 1),
  (3, '王VP(产品)', 1),
  (4, '赵经理(后端)', 2),
  (5, '钱经理(前端)', 2),
  (6, '孙经理(数据)', 3),
  (7, '员工A', 4),
  (8, '员工B', 4),
  (9, '员工C', 6),
  (10, '员工D', 6);
""")

# 2. ASOF JOIN：报价 + 交易
con.execute("""
CREATE TABLE quotes (symbol VARCHAR, quote_time TIMESTAMP, price DECIMAL(10,2));
CREATE TABLE trades (trade_time TIMESTAMP, symbol VARCHAR, qty INTEGER);
INSERT INTO quotes VALUES
  ('AAPL', '2024-01-01 09:00:00', 180.00),
  ('AAPL', '2024-01-01 09:05:00', 181.50),
  ('AAPL', '2024-01-01 09:10:00', 182.00),
  ('GOOG', '2024-01-01 09:00:00', 140.00),
  ('GOOG', '2024-01-01 09:06:00', 141.00);
INSERT INTO trades VALUES
  ('2024-01-01 09:03:00', 'AAPL', 100),
  ('2024-01-01 09:08:00', 'AAPL', 50),
  ('2024-01-01 09:04:00', 'GOOG', 30);
""")

# 导出 employees 到 duckdb 文件供 app 使用（内存表进程退出即失）
con.execute(f"COPY employees TO '{os.path.join(DATA, 'employees.parquet')}' (FORMAT PARQUET)")

# 3. JSON 事件文件
events = [
    {"event_id": 1, "user": {"name": "张三", "vip": True}, "action": "purchase", "items": [{"id": 101, "price": 199.0}, {"id": 102, "price": 299.0}]},
    {"event_id": 2, "user": {"name": "李四", "vip": False}, "action": "view", "items": [{"id": 101, "price": 199.0}]},
    {"event_id": 3, "user": {"name": "王五", "vip": True}, "action": "purchase", "items": [{"id": 103, "price": 399.0}]},
]
with open(os.path.join(DATA, "events.json"), "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

print("=== 高级特性演示数据已生成 ===")
print("employees 层级：10 人")
print("quotes/trades：ASOF JOIN 用")
print("events.json：3 条嵌套 JSON 事件")
