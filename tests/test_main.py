import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.ticket_page import TicketPage

# uv run python -m pytest ./tests/test_main.py --headed --html=./report/report.html --self-contained-html

# page是一个fixture
def test_gym(page: Page, config):
    cfg = config
    
    # 登录
    login_page = LoginPage(page)
    login_page.login(cfg['username'], cfg['password'])

    # 预订场地
    ticket_page = TicketPage(page)
    # 使用括号 ( ... ) 可以让整个表达式自动支持换行
    (ticket_page
        .select_campus()
        .select_venue(cfg['venue'])
        .select_date(cfg['date'], cfg['venue'], wait_timeout_seconds=int(cfg['wait_timeout_seconds']))
        .select_time_slot(cfg['time_slot'])
        .select_specific_venue(cfg['venue'], cfg.get('court'))
        .submit_booking()
        .make_payment(cfg['pay_pass'])
        .verify_payment_success()
    )