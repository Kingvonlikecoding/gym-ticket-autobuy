import pytest
import re
from playwright.sync_api import Page, expect,TimeoutError
import random

# uv run python -m pytest ./tests/test_buy_ticket.py

def test_badminton(page: Page, config):
    cfg = config

    # Arrange
    page.goto("https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do#/sportVenue")

    # Act_Login
    page.locator("//section//input[@id='username']").fill(cfg['username'])
    page.locator("//section//input[@id='password']").fill(cfg['password'])
    thetime = cfg['time_slot']
    page.locator("//section//a[@id='login_submit']").click()


    # Act_Navigation
    page.wait_for_load_state('load')  # 等待整个页面加载完成
    page.click("div.bh-btn-primary:has-text('粤海校区')")

    # 羽毛球
    page.wait_for_selector("img.union-2[src*='317a6df934914473b49996840b305987']", timeout=10000)
    page.click("img.union-2[src*='317a6df934914473b49996840b305987']")

    from datetime import date, timedelta
    today = date.today()
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime(f"%Y-%m-%d")  # 输出 "2025-05-08"

    target_selector = "//label/div[contains(.,'" + tomorrow_str + "')]"  # 使用XPath选择器来匹配包含日期的元素
    max_attempts = 10  # 总共尝试次数：初始页面加载 + 9次刷新 = 10次
    wait_timeout_seconds = 10 # 每次尝试等待元素出现的最大秒数

    for attempt in range(max_attempts):

        if attempt > 0:
            # Act_Navigation
            page.wait_for_load_state('load')  # 等待整个页面加载完成
            page.click("div.bh-btn-primary:has-text('粤海校区')")

            # 羽毛球
            page.wait_for_selector("img.union-2[src*='317a6df934914473b49996840b305987']", timeout=10000)
            page.click("img.union-2[src*='317a6df934914473b49996840b305987']")

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

    # 羽毛球
    available_venue_selector = "div.element:has-text('可预约')"

    # Find all elements that match the selector
    available_venues = page.locator(available_venue_selector).all()

    # Filter for visible elements
    visible_available_venues = [
        venue for venue in available_venues if venue.is_visible()
    ]

    if not visible_available_venues:
        raise RuntimeError("无体育场馆了")

    # Select one visible available venue randomly
    chosen_venue = random.choice(visible_available_venues)

    # Get the text of the chosen venue for logging
    chosen_venue_text = chosen_venue.text_content()
    print(f"  Randomly selected venue: '{chosen_venue_text}'. Clicking...")

    # Click the chosen venue
    chosen_venue.click()

    page.click("button.bh-btn.bh-btn-default.bh-btn-large:has-text('提交预约')")

    # Pay
    page.click("a:has-text('未支付')")
    page.click("button:has-text('(剩余金额)支付')")


    # Assert
    expect(page.get_by_text('支付成功')).to_be_visible()
    print("✅ 支付成功提示已显示！")


    # Close the browser: playwright自动关闭