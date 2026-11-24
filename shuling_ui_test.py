# shuling_ui_test.py
from playwright.sync_api import Page, expect
from config import LOGIN_URL


def test_shuling_ui(page: Page) -> None:
    print("\n🚀 开始执行 UI 自动化测试...")

    # 保险：若 fixture 停的不是 chat 页（极少见），goto LOGIN_URL 会自动跳转过去
    if "/bizmodule/bteam/home/chat.htm" not in page.url:
        page.goto(LOGIN_URL)
        page.wait_for_load_state("networkidle")

    # ---------------- 以下是你录制的自动化操作 ----------------

    # 1. 点击「更多」
    more_btn = page.get_by_role("button", name="更多")
    more_btn.wait_for(state="visible", timeout=20000)
    more_btn.click()

    # 2. 点击「书灵AI」
    shuling_btn = page.get_by_role("button", name="书灵AI")
    shuling_btn.wait_for(state="visible", timeout=20000)
    shuling_btn.click()

    # 3. 等待 iframe 加载并点击下拉框
    iframe = page.frame_locator("iframe")
    combobox = iframe.get_by_role("combobox", name="题目属性 :")
    combobox.wait_for(state="visible", timeout=20000)
    combobox.click()

    # 4. 断言下拉框包含「常规题」
    dropdown = iframe.locator(".yt5-antd-select-dropdown")
    expect(dropdown.get_by_text("常规题", exact=True)).to_be_visible(timeout=1000)
    print("✅ 测试断言通过！")