import pytest
from playwright.sync_api import Page
import time

from pages.login_page import LoginPage

# uv run python -m pytest ./tests/test_main.py --headed --html=./report/report.html --self-contained-html

# page是一个fixture
def test_gym(page: Page, config):
    cfg = config
    
    # 登录
    login_page = LoginPage(page)
    if login_page.login(cfg['username'], cfg['password']):
        # 登录成功，继续后续操作
        try:
            while(1):
                time.sleep(3)
                page.title()
        except:
            pass
    else:
        # 登录失败，处理失败情况
        pass
