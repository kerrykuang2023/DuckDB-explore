# Rule: R-01 数据源联邦
# 一个 DuckDB 进程能连接多个异构数据源，用户可选任一数据源查询

Feature: 数据源联邦

  Scenario: 连接并展示多个数据源
    Given DuckDB 已连接 SQLite 数据源 edu_orders.db（含 courses/students/orders/reviews 4 张表）
    And DuckDB 已连接 SQLite 数据源 Walmart_Sales.db（含 walmart_sales 表）
    And DuckDB 已连接 CSV 数据源 courses_dim.csv
    When 用户在 UI 上查看可用的数据源列表
    Then UI 展示 3 个数据源：edu_orders、Walmart_Sales、courses_dim
    And 每个数据源显示其表/文件数量

  @use-case
  Scenario: 选择数据源查询
    Given DuckDB 已连接 edu_orders 数据源
    When 用户在 UI 上选择 edu_orders 并触发查询
    Then UI 返回 edu_orders 中 courses 表的行数（10 行）
    And UI 展示查询耗时（毫秒级）

  @technical
  Scenario: 不支持的数据源类型
    Given 用户尝试连接一个不存在的文件路径
    When 触发查询
    Then UI 显示清晰的错误提示（文件不存在）
