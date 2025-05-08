import pytest
import re
import json
from playwright.sync_api import Page, expect,TimeoutError

# uv run python -m pytest ./tests/test_buy_ticket.py

def test_basketball(page: Page, config):
    cfg = config

    # Arrange
    page.goto("https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do#/sportVenue")

    # Act_Login
    page.locator("//section//input[@id='username']").fill(cfg['username'])
    page.locator("//section//input[@id='password']").fill(cfg['password'])
    thetime = cfg['time']
    page.locator("//section//a[@id='login_submit']").click()


    # Act_Navigation
    page.wait_for_load_state('load')  # 等待整个页面加载完成
    page.click("div.bh-btn-primary:has-text('粤海校区')")

    # 篮球
    page.wait_for_selector("img.union-2[src*='eaaf3fd0bf624a328966f987fcd0ac52']", timeout=10000)
    page.click("img.union-2[src*='eaaf3fd0bf624a328966f987fcd0ac52']")

    from datetime import date, timedelta
    today = date.today()
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")  # 输出 "2025-05-08"

    target_selector = f"div.element:has-text('{tomorrow_str}')"
    max_attempts = 10  # 总共尝试次数：初始页面加载 + 9次刷新 = 10次
    wait_timeout_seconds = 10 # 每次尝试等待元素出现的最大秒数
    print(f"Attempting to find and click date '{tomorrow_str}' with selector '{target_selector}'")

    for attempt in range(max_attempts):

        if attempt > 0:
            # Act_Navigation
            page.wait_for_load_state('load')  # 等待整个页面加载完成
            page.click("div.bh-btn-primary:has-text('粤海校区')")

            # 篮球
            page.wait_for_selector("img.union-2[src*='eaaf3fd0bf624a328966f987fcd0ac52']", timeout=10000)
            page.click("img.union-2[src*='eaaf3fd0bf624a328966f987fcd0ac52']")

            from datetime import date, timedelta
            today = date.today()
            tomorrow = today + timedelta(days=1)
            tomorrow_str = tomorrow.strftime("%Y-%m-%d")  # 输出 "2025-05-08"

            target_selector = f"div.element:has-text('{tomorrow_str}')"
            max_attempts = 10  # 总共尝试次数：初始页面加载 + 9次刷新 = 10次
            wait_timeout_seconds = 10 # 每次尝试等待元素出现的最大秒数
            print(f"Attempting to find and click date '{tomorrow_str}' with selector '{target_selector}'")


        try:
            # 使用 locator.wait_for() 来等待元素可见
            # timeout 参数以毫秒为单位
            date_locator = page.locator(target_selector)
            date_locator.wait_for(state='visible', timeout=wait_timeout_seconds * 1000)

            # 如果 wait_for 没有抛出异常，说明元素在规定时间内出现了
            date_locator.click()
            break # 元素找到并点击成功，跳出循环

        except TimeoutError:
            # 如果 wait_for 超时，捕获 TimeoutError 异常
            if attempt < max_attempts - 1:
                # 如果还没达到最大尝试次数，则刷新页面并继续下一次尝试
                page.reload()
            else:
                # 已经达到最大尝试次数，仍然没有找到元素，则报错
                print("Maximum attempts reached. Element not found after multiple refreshes.")
                raise RuntimeError(f"时间未到或没票了: Failed to find and click date '{tomorrow_str}' after {max_attempts} attempts.")

    page.click(f"div.element:has-text('{thetime}')")  # 点击时间段

    # 篮球
    page.wait_for_selector("div.element:has-text('东馆篮球4号场(')", timeout=10000)
    page.click("div.element:has-text('东馆篮球4号场(')")

    page.click("button.bh-btn.bh-btn-default.bh-btn-large:has-text('提交预约')")

    # Pay
    page.click("a:has-text('未支付')")
    page.click("button:has-text('(剩余金额)支付')")


    # Assert
    expect(page.get_by_text('支付成功')).to_be_visible()
    print("✅ 支付成功提示已显示！")


    # Close the browser: playwright自动关闭