# conftest.py
import os
import pytest
from playwright.sync_api import sync_playwright, Page
from config import STATE_FILE, LOGIN_URL, HEADLESS


@pytest.fixture(scope="session")
def page() -> Page:
    """整个测试会话共用一个 page / context / browser。"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)

        # ---------- 分支 A：有 state.json，加载并校验 ----------
        if os.path.exists(STATE_FILE):
            print(f"\n✅ 检测到 {STATE_FILE}，自动加载登录状态...")
            context = browser.new_context(storage_state=STATE_FILE)
            pg = context.new_page()

            # 已登录 → login 页会自动重定向到 chat.htm
            pg.goto(LOGIN_URL)
            pg.wait_for_load_state("networkidle")

            # 若 URL 还停在 login，说明状态失效
            if "login" in pg.url.lower():
                pg.screenshot(path="login_expired.png")
                context.close()
                browser.close()
                raise RuntimeError(
                    f"❌ 登录状态已失效（当前 URL={pg.url}）。"
                    f"请先运行 save_state.py 重新生成 {STATE_FILE}"
                )

        # ---------- 分支 B：没有 state.json，手动登录并保存 ----------
        else:
            print(f"\n⚠️  未检测到 {STATE_FILE}，请在弹出的浏览器中手动登录！")
            context = browser.new_context()
            pg = context.new_page()
            pg.goto(LOGIN_URL)
            print("请手动输入手机号和验证码，登录成功后会自动保存状态...")

            pg.wait_for_url("**/bizmodule/bteam/home/chat.htm", timeout=180000)
            pg.wait_for_load_state("networkidle")
            context.storage_state(path=STATE_FILE)
            print(f"✅ 登录成功！状态已保存至 {STATE_FILE}")

        yield pg

        context.close()
        browser.close()