# Rule: R-08 单进程多线程读
# DuckDB 在单进程内完成多个查询，无需启动外部服务

Feature: 单进程多线程读

  @use-case
  Scenario: 单进程内完成多个独立查询
    Given DuckDB-explore UI 运行在一个进程内
    When 用户依次触发 3 个独立查询（edu_orders 行数、Walmart TOP5、跨源 JOIN）
    Then 3 个查询全部成功返回
    And 全程仅一个进程（无额外 worker/coordinator 进程）

  @technical
  Scenario: 查询不依赖外部服务
    Given DuckDB-explore UI 已启动
    When 用户连续触发查询
    Then 查询无需连接任何外部数据库服务即可完成
