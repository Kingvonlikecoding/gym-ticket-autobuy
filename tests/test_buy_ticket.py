import pytest
import re
import json
from playwright.sync_api import Page, expect

# uv run python -m pytest ./tests/test_buy_ticket.py

def test_gymticket_buying(page: Page):

    # Arrange
    page.goto("https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do#/sportVenue")

    # Act_Login
    with open("config/settings.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    page.locator("//section//input[@id='username']").fill(config['username'])
    page.locator("//section//input[@id='password']").fill(config['password'])
    page.locator("//section//a[@id='login_submit']").click()

    # Act_Navigation
    page.wait_for_load_state('load')  # 等待整个页面加载完成
    page.click("div.bh-btn-primary:has-text('粤海校区')")

    # # 健身房
    # page.wait_for_selector("img.union-2[src*='6cf6b63b970a4f4b87193d799d8092c7']", timeout=10000)
    # page.click("img.union-2[src*='6cf6b63b970a4f4b87193d799d8092c7']")

    # 篮球
    page.wait_for_selector("img.union-2[src*='eaaf3fd0bf624a328966f987fcd0ac52']", timeout=10000)
    page.click("img.union-2[src*='eaaf3fd0bf624a328966f987fcd0ac52']")

    page.click("div[style='color: rgb(29, 33, 41);']")
    page.click("div.element:has-text('20:00-21:00')")

    # # 健身房
    # page.wait_for_selector("div.element:has-text('一楼健身房(')", timeout=10000)
    # page.click("div.element:has-text('一楼健身房(')")

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

