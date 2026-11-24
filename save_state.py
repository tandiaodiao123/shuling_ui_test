# save_state.py
import os
from playwright.sync_api import sync_playwright
from config import STATE_FILE, LOGIN_URL


def main():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print(f"🗑️  已删除旧的 {STATE_FILE}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)   # 存状态必须有头
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL)
        print("👉 请在弹出的浏览器中手动完成登录（手机号 + 验证码）...")

        # 登录成功后自动跳转到 chat.htm
        page.wait_for_url("**/bizmodule/bteam/home/chat.htm", timeout=180000)
        page.wait_for_load_state("networkidle")

        # 双保险：等「更多」按钮出现
        page.get_by_role("button", name="更多").wait_for(state="visible", timeout=20000)
        print(f"✅ 已进入工作台: {page.url}")

        context.storage_state(path=STATE_FILE)
        print(f"✅ 登录状态已保存到 {STATE_FILE}")

        browser.close()


if __name__ == "__main__":
    main()