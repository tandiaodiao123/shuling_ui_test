# 用例覆盖映射

用例 ID → 脚本位置的唯一索引。新增、修改、删除用例时同步维护本表；
删除失效用例时连同映射一起删除，不允许只加不减。

| 用例 ID | 端 | 场景 | 文件 | 函数 | 状态 | 最近更新 |
|---|---|---|---|---|---|---|
| CASE_WEB_001 | Web | 工作台入口 → 书灵AI → 题型下拉选项可见 | `shuling_ui_test.py` | `test_shuling_ui` | 已入库（历史） | 2026-11-24 |
| CASE_WEB_573_01 | Web | 反馈列表列顺序且无「最近编辑」（T-01） | `tests/web/test_shuling_573_admin.py` | `test_t01_feedback_columns` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_02 | Web | 分配/处理时间显示操作人（T-02） | `tests/web/test_shuling_573_admin.py` | `test_t02_assign_and_process_operator` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_03 | Web | 题库 12 列与题型/母题标签（T-08） | `tests/web/test_shuling_573_admin.py` | `test_t08_question_bank_columns_and_tags` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_04 | Web | 题库顶部四项搜索与重置（T-09） | `tests/web/test_shuling_573_admin.py` | `test_t09_question_bank_search` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_05 | Web | 操作栏上下架展示（T-10） | `tests/web/test_shuling_573_admin.py` | `test_t10_shelf_actions` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_06 | Web | 驳回次数区间筛选（T-11） | `tests/web/test_shuling_573_admin.py` | `test_t11_reject_count_range` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_07 | Web | 驳回次数非法区间提示（T-13） | `tests/web/test_shuling_573_admin.py` | `test_t13_reject_count_invalid_range` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_08 | Web | 空结果筛选与清除（T-14） | `tests/web/test_shuling_573_admin.py` | `test_t14_empty_filter_result` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_09 | Web | 筛选接口失败保留旧结果（T-17） | `tests/web/test_shuling_573_admin.py` | `test_t17_filter_api_failure_keeps_old_result` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_10 | Web | 多选枚举并集/交集语义（T-21） | `tests/web/test_shuling_573_admin.py` | `test_t21_multi_select_union` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_11 | Web | 切换学段清空题型（T-22） | `tests/web/test_shuling_573_admin.py` | `test_t22_subject_switch_clears_type` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_12 | Web | 四入口 1440×900 无横向溢出（T-27） | `tests/web/test_shuling_573_admin.py` | `test_t27_four_entries_no_overflow_at_1440` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_13 | Web | 题库列表深链直达（T-29） | `tests/web/test_shuling_573_admin.py` | `test_t29_question_bank_deep_link` | 待人工验证 | 2026-11-25 |
| CASE_WEB_573_14 | Web | 错误明细错误原因单选与筛选（T-12） | `tests/web/test_shuling_573_admin.py` | `test_t12_error_detail_single_reason_filter` | 待人工验证 | 2026-11-26 |
| CASE_WEB_573_15 | Web | 题库 1280×720 表头对齐与横向滚动（T-19） | `tests/web/test_shuling_573_admin.py` | `test_t19_question_bank_1280_alignment` | 待人工验证 | 2026-11-26 |
| CASE_WEB_573_16 | Web | 切换错误分类重置错误原因（T-20） | `tests/web/test_shuling_573_admin.py` | `test_t20_error_category_switch_resets_reason` | 待人工验证 | 2026-11-26 |

状态取值：已入库 / 待人工验证 / 已废弃。

维护约定：

1. 新增脚本时追加一行，用例 ID 与脚本注释中的编号一致。
2. 函数改名或文件迁移时更新对应行。
3. 用例因页面改版失效且不打算修复时，标“已废弃”并在下一轮清理中删除。
