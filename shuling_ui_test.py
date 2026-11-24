# shuling_ui_test.py
import re

from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from config import LOGIN_URL

# 「进入工作台」会新开标签页，落在这个路径上
WORKBENCH_PATH = "/bizmodule/aiTutorWeb/auditWorkBench.htm"
# 题库列表加载完成的标志：底部「共 N 条数据」
LIST_READY = re.compile(r"共\s*\d+\s*条数据")


def test_shuling_ui(page: Page) -> None:
    print("\n🚀 开始执行 UI 自动化测试...")

    # 保险：若 fixture 停的不是 chat 页（极少见），goto LOGIN_URL 会自动跳转过去
    if "/bizmodule/bteam/home/chat.htm" not in page.url:
        page.goto(LOGIN_URL, wait_until="commit")
        page.wait_for_url("**/bizmodule/bteam/home/chat.htm", timeout=180000)

    # ---------------- 以下是你录制的自动化操作 ----------------

    # 1. 点击「更多」
    more_btn = page.get_by_role("button", name="更多")
    more_btn.wait_for(state="visible", timeout=120000)
    more_btn.click()

    # 2. 点击「书灵AI」→ 打开题库页（在 iframe 里）
    shuling_btn = page.get_by_role("button", name="书灵AI")
    shuling_btn.wait_for(state="visible", timeout=120000)
    shuling_btn.click()

    # 3. 等题库列表真正加载出数据
    #    点太早会进到「共 0 道题」的空工作台，右侧没有「题型」下拉
    question_bank = page.frame_locator("iframe")
    total = question_bank.get_by_text(LIST_READY)
    try:
        total.first.wait_for(state="visible", timeout=180000)
    except PlaywrightTimeoutError:
        raise AssertionError(
            "题库列表未加载出数据（列表为空或接口 401，多半是登录态失效）。"
            f"当前页面片段：{question_bank.locator('body').inner_text(timeout=5000)[:200]!r}"
        )
    print(f"   题库列表已加载：{total.first.inner_text()}")

    # 4. 点「进入工作台」：会新开一个「审核题目」标签页
    enter_btn = question_bank.get_by_role("button", name="进入工作台")
    with page.context.expect_page() as new_page_info:
        enter_btn.click()
    workbench = new_page_info.value

    # 5. 审核页有长轮询 / 二次跳转，等 load 事件不可靠，直接等右侧「题型」下拉出现
    #    （旧版这块文案是「题目属性」，选项集也已改版）
    type_select = workbench.locator(".yt5-antd-select").first
    type_select.wait_for(state="visible", timeout=120000)
    assert WORKBENCH_PATH in workbench.url, f"未进入审核工作台，当前 URL={workbench.url}"
    assert "id=" in workbench.url, f"工作台未带上题目 ID，可能是空列表：{workbench.url}"

    # 6. 点击「题型」下拉，断言展开后包含现行选项
    type_select.click()
    dropdown = workbench.locator(".yt5-antd-select-dropdown")
    dropdown.wait_for(state="visible", timeout=10000)
    expect(dropdown.get_by_text("单选", exact=True)).to_be_visible(timeout=5000)
    print("✅ 测试断言通过！")
