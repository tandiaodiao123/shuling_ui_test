import pytest
from playwright.sync_api import sync_playwright, Page, expect
import os

# 你的状态文件路径
STATE_FILE = "state.json"


@pytest.fixture(scope="session")
def page():
    with sync_playwright() as p:
        # 1. 启动浏览器（注意：不再使用 launch_persistent_context）
        browser = p.chromium.launch(headless=True)  # 本地调试用 False，云端跑可改为 True

        # 2. 判断是否有已有的登录状态
        if os.path.exists(STATE_FILE):
            print(f"\n✅ 检测到 {STATE_FILE}，自动加载登录状态...")
            # 核心：通过 storage_state 加载状态
            context = browser.new_context(storage_state=STATE_FILE)
            page = context.new_page()
        else:
            print(f"\n⚠️ 未检测到 {STATE_FILE}，请在弹出的浏览器中手动登录！")
            context = browser.new_context()
            page = context.new_page()

            # 打开登录页
            page.goto("https://www-daily.yuntim.com/bizmodule/bteamLogin/login.htm")
            print("请手动输入手机号和验证码，登录成功后会自动保存状态...")

            # 智能等待：等待跳转到目标工作台页面（最多等 60 秒，给你足够的时间收验证码）
            # 这样做比死等 30 秒更智能
            page.wait_for_url("**/bizmodule/bteam/home/chat.htm", timeout=60000)

            # 登录成功后，保存状态到文件
            context.storage_state(path=STATE_FILE)
            print(f"✅ 登录成功！状态已保存至 {STATE_FILE}")

        yield page

        # 测试结束后清理
        context.close()
        browser.close()


def test_shuling_ui(page: Page) -> None:
    # 因为 fixture 已经处理了登录逻辑，这里我们直接去目标页面
    print("\n🚀 开始执行 UI 自动化测试...")
    page.goto("https://www-daily.yuntim.com/bizmodule/bteam/home/chat.htm")

    # ---------------- 以下是你录制的自动化操作 ----------------

    # 等待页面加载完成
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="更多").click()
    page.get_by_role("button", name="书灵AI").click()

    # 正确标准的 iframe 定位方式
    iframe = page.frame_locator("iframe")

    # 1. 点击下拉框
    iframe.get_by_role("combobox", name="题目属性 :").click()

    # 2. 先定位到下拉菜单的容器
    dropdown = iframe.locator(".yt5-antd-select-dropdown")

    # 3. 在这个容器里断言包含“常规题”的选项可见
    expect(dropdown.get_by_text("常规题", exact=True)).to_be_visible()
    print("✅ 测试断言通过！")