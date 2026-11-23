# Rule: R-07 资源轻量提示
# UI 展示 DuckDB 为嵌入式、无 server、单进程轻量运行的说明

Feature: 资源轻量提示

  @ui
  Scenario: 展示嵌入式特性说明
    Given 用户打开 DuckDB-explore UI
    When 页面加载完成
    Then UI 展示信息卡片，说明 DuckDB 为嵌入式、无 server、单进程轻量运行
    And 卡片内容包含"无独立 server 进程"与"内存占用 < 1GB"两项说明

  @technical
  Scenario: 无外部服务依赖
    Given 用户已启动 DuckDB-explore UI
    When 用户执行查询
    Then 查询在 UI 进程内完成
    And 无需要额外启动的数据库服务（除 UI 进程外无独立 DB server）
