# Rule: R-02 跨源 JOIN
# 跨两个不同来源做关联查询，用户点选关联键，无需手写 JOIN 语法

Feature: 跨源 JOIN

  @use-case
  Scenario: SQLite 表 + CSV 维度表跨源 JOIN
    Given DuckDB 已连接 edu_orders（SQLite，含 orders 表：course_id）
    And DuckDB 已连接 courses_dim.csv（含 course_id 和 course_name 列）
    When 用户在 UI 上选择 orders.course_id 与 courses_dim.course_id 关联
    And 触发"按课程统计订单数"查询
    Then UI 返回每门课程对应的订单数
    And 结果中 course_name 来自 CSV，订单数来自 SQLite

  @technical
  Scenario: 跨源 JOIN 关联键不匹配
    Given 用户在 UI 上选择 orders.student_id 与 courses_dim.course_id 关联（键类型不匹配）
    When 触发查询
    Then UI 显示关联键不匹配的提示，而非静默返回错误结果
