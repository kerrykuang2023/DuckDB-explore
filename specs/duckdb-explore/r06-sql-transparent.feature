# Rule: R-06 SQL 透明可查
# 虽不用用户写 SQL，但 UI 需展示 DuckDB 实际执行的 SQL（只读展示）

Feature: SQL 透明可查

  @ui
  Scenario: 展示底层执行的 SQL
    Given 用户在 UI 上点选字段和聚合操作（而非手写 SQL）
    When 触发查询
    Then UI 展示 DuckDB 实际执行的 SQL 语句（只读，灰色代码块）
    And 该 SQL 与用户点选的操作一致（如点选"按 Store 分组 + SUM"对应 GROUP BY Store）

  @technical
  Scenario: SQL 展示为只读不可编辑
    Given UI 展示了底层 SQL
    When 用户尝试直接编辑该 SQL 文本
    Then UI 不接受编辑（SQL 仅作透明展示，交互通过点选完成）
