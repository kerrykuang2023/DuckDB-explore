import sqlite3, csv
c = sqlite3.connect(r"E:\codespace\ghub-projects\dbgpt-run\edu_orders.db")
rows = c.execute("SELECT course_id, course_name, category, price, instructor FROM courses").fetchall()
with open(r"E:\codespace\ghub-projects\DuckDB-explore\data\courses_dim.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["course_id", "course_name", "category", "price", "instructor"])
    w.writerows(rows)
print("courses_dim.csv rows:", len(rows))
