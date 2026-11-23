# Rule: R-03 无 ETL 直查
# 直接读取外部文件/库，不要求用户先建表或导入数据

Feature: 无 ETL 直查

  @use-case
  Scenario: 直接查询外部 CSV 文件
    Given 项目目录 data/ 下存在 walmart_sales_sample.csv
    When 用户在 UI 上选择该 CSV 文件并触发查询
    Then UI 直接返回该 CSV 的前 5 行数据
    And 全程无需用户执行任何建表或导入操作

  @use-case
  Scenario: 直接查询外部 SQLite 文件
    Given DuckDB 已通过 ATTACH 连接 edu_orders.db
    When 用户查询 courses 表行数
    Then UI 返回 10 行
    And 数据仍在原文件 edu_orders.db 中（未被复制进 DuckDB）
