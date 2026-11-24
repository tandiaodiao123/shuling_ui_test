# verify_state.py
import os
from playwright.sync_api import sync_playwright
from config import STATE_FILE, LOGIN_URL


def main():
    if not os.path.exists(STATE_FILE):
        raise SystemExit(f"❌ {STATE_FILE} 不存在，请先运行 save_state.py")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        # 已登录时会从 login 页自动跳到工作台
        page.goto(LOGIN_URL)
        page.wait_for_load_state("networkidle")
        page.screenshot(path="verify_state.png")

        print("当前 URL =", page.url)
        if "login" in page.url.lower():
            print("❌ 登录状态无效，请重新运行 save_state.py")
        else:
            print("✅ 登录状态有效，截图已保存 verify_state.png")

        browser.close()


if __name__ == "__main__":
    main()