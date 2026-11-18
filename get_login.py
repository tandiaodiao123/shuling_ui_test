from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    # 检查有没有保存过状态文件
    if os.path.exists("state.json"):
        print("检测到登录状态，自动加载...")
        context = browser.new_context(storage_state="state.json")
    else:
        print("首次运行，请手动登录...")
        context = browser.new_context()

    page = context.new_page()
    page.goto("https://www-daily.yuntim.com/bizmodule/bteam/home/app.htm?code=robot:20251124180148_4w6ap")

    # 如果是首次运行，给时间让你手动登录
    if not os.path.exists("state.json"):
        page.wait_for_timeout(30000)  # 留 30 秒给你扫码/输密码
        context.storage_state(path="state.json")  # 保存状态
        print("登录状态已保存！")

    browser.close()