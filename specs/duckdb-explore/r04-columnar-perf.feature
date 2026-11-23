# Rule: R-04 列式向量化性能可见
# 每次查询展示实际耗时（毫秒级），证明列式 + 向量化执行的分析性能

Feature: 列式向量化性能可见

  @use-case
  Scenario: 聚合查询耗时可见
    Given DuckDB 已连接 Walmart_Sales（walmart_sales 表，6435 行）
    When 用户在 UI 上触发"按 Store 统计总周销售额 TOP5"查询
    Then UI 展示查询结果
    And UI 展示该查询的耗时（单位：毫秒）

  @limit
  Scenario: 聚合查询耗时应低于阈值
    Given DuckDB 已连接 Walmart_Sales
    When 用户触发"按 Store 分组 SUM(Weekly_Sales) 排序"查询
    Then 该查询耗时 < 100 毫秒（单机列式向量化，6435 行规模）
