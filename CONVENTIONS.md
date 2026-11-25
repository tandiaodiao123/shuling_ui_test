# 书灵 AI UI 自动化 · 仓库编码约定

适用范围：本仓库全部 Python + pytest + Playwright 代码。
新增或修改代码前先读本文件；与本文冲突的写法以本文为准。
本文件是规范事实源，`欧拉` 的提示词只引用、不复制。

## 1. 目录结构

```
shuling_ui_test/
├── config.py             # 环境、URL、角色、超时集中配置
├── conftest.py           # 全局 fixture（登录态、page、context）
├── save_state.py         # 人工登录并保存 state.json（不用于测试）
├── verify_state.py       # 校验 state.json 是否仍有效
├── shuling_ui_test.py    # 历史主流程用例，保留兼容
├── tests/
│   ├── web/              # Web 用例，test_<模块>_<功能>.py
│   └── h5/               # H5 用例（移动模拟）
├── pages/                # 页面对象，一个页面一个文件
├── utils/                # 公共方法：iframe、新标签页、等待、数据
├── docs/                 # 报告模板等文档
├── COVERAGE.md           # 用例 ID → 文件 → 函数 映射
└── reports/              # 运行产物，不入库
```

演进规则：**只有同一页面/方法被第二个文件复用时**，才抽到 `pages/` 或 `utils/`。不提前造框架，不为“整洁”重构已有脚本。

## 2. 命名

| 对象 | 规则 | 示例 |
|---|---|---|
| 测试文件 | `test_<模块>_<功能>.py` | `test_review_workbench.py` |
| 测试函数 | `test_<场景>_<预期>`，snake_case，中文场景写注释 | `test_open_question_type_dropdown` |
| 页面对象 | `<页面>Page`，文件 `<页面>_page.py` | `class ReviewPage` / `review_page.py` |
| 页面方法 | 用户视角动作，不用实现细节 | `open_shuling_ai()`、`select_question_type()` |
| fixture | session 级保留 `page`；新用例用函数级 `new_page` | — |
| 用例 ID | 常量或注释，形如 `CASE_WEB_001` | `# CASE_WEB_001：...` |

## 3. 定位

优先级：

1. `get_by_role(...)`
2. `get_by_label(...)` / `get_by_text(...)`（需要时加 `exact=True`）
3. `get_by_test_id(...)`
4. CSS

禁止：绝对 XPath、`nth-child` 长链、坐标点击、MCP 临时元素引用、依赖元素顺序的下标定位。

iframe：

```python
iframe = page.frame_locator("iframe")
iframe.get_by_role("combobox", name="题型").click()
```

跨 frame 不混用 locator；`frame_locator` 在函数内声明一次复用。

新标签页：

```python
with page.context.expect_page() as new_page_info:
    page.get_by_role("button", name="进入工作台").click()
workbench = new_page_info.value
workbench.wait_for_load_state("domcontentloaded")
```

## 4. 等待与断言

- 禁止把 `time.sleep()` / `wait_for_timeout()` 当主要等待手段；只可用于极短的 UI 动画兜底，且需注释原因。
- 优先 `expect(locator).to_be_visible(timeout=...)`、`to_have_text()`、`to_have_count()`、`to_contain_text()`。
- 页面跳转用 `page.wait_for_url("**/chat.htm")`；本项目首屏 `app.htm → chat.htm`，等 URL 不要等固定时长。
- **不用 `networkidle` 作为唯一判据**（站点有长轮询，可能长期不静默）。
- 每个测试函数至少一个业务断言；只点击不断言不计为通过。
- 断言业务结果（列表有数据、状态变更、文案正确），不用“元素可见”凑数。

## 5. 登录态

- `state.json` 由 `save_state.py` 人工登录生成；代码只引用 `config.STATE_FILE`。
- 缺失时明确报错并提示人工执行 `save_state.py`，**不自动登录、不代填验证码**。
- 禁止在代码、配置、注释、提交中出现 cookie、token、手机号、验证码。
- `state.json` 不入库（见 `.gitignore`）。

## 6. 用例隔离

- 新用例用函数级 `new_page`：独立 context + 加载 `storage_state`，用完即关。
- 不依赖上一函数留下的页面状态；需要入口就自己 `goto`。
- 同一文件内可共享只读数据（常量、参数化列表），不共享可变页面状态。

## 7. 测试数据

- 数据集中放 `tests/data/` 或 `utils/data.py`，不散落魔法字符串。
- 新建数据带可识别前缀（如 `QA_AUTO_`）；需求允许时在使用后清理。
- 不操作与本次任务无关的业务数据；涉及删除、提交只对测试数据做。

## 8. 注释与证据

- 每个关键操作和断言前：`# CASE_WEB_001：打开题型下拉并校验选项`。
- 文件头可写覆盖清单，但不能替代步骤注释。
- 业务脚本不加截图命令；失败截图沿用 `conftest.py` 既有机制。
- 截图命名：`CASE_WEB_001-01-open-dropdown.png`，独立文件，不打包。

## 9. 提交与合入

- 提交说明：`test(web): 场景描述 [TASK-xxx]`；无任务号用需求名称。修复 CI 用 `fix(ci): ...`。
- 一个任务一个提交；只 `git add` 明确文件，**禁用 `git add -A`**。
- 推送前 `git fetch` + `git rebase origin/develop`；只合 `develop`，不 force push，不碰 `main`。
- 提交前检查 diff 是否含敏感信息与无关文件。
- 禁入提交：`state.json`、`reports/`、截图、日志、`.idea/`、`__pycache__/`。

## 10. 入库前自检

```bash
python -m compileall -q .
pytest --collect-only -q
```

两项必须通过才允许提交。真实冒烟默认不做；用户显式授权时最多跑一次新增文件，失败只记录、不进入排障循环。
