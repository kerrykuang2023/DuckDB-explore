# Rule: R-05 结果可视化
# 查询结果以表格 + 图表呈现，而非只显示原始 SQL 文本

Feature: 结果可视化

  @ui
  Scenario: 聚合结果以表格和图表展示
    Given 用户已触发"按课程分类统计订单数"查询
    When 查询返回结果
    Then UI 以表格展示每个分类的订单数
    And UI 以柱状图展示同样的数据
    And UI 不要求用户阅读 SQL 文本来理解结果

  @ui
  Scenario: 指标卡展示关键数字
    Given 用户已触发"统计总订单数"查询
    When 查询返回结果
    Then UI 以指标卡（metric）展示总订单数
