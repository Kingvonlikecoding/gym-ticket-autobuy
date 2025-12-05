import pytest
import json
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.ticket_page import TicketPage

# page是一个fixture
def test_gym(page: Page, config):
    cfg = config
    
    # 登录
    login_page = LoginPage(page)
    login_page.login(cfg['username'], cfg['password'])

    # 预订场地
    ticket_page = TicketPage(page)
    # 使用括号 ( ... ) 可以让整个表达式自动支持换行
    leftover_timeslots = (ticket_page
        .select_campus()
        .select_venue(cfg['venue'])
        .select_date(cfg['date'], cfg['venue'], wait_timeout_seconds=float(cfg['wait_timeout_seconds']))
        .leftover_timeslot()
    )
    
    # 将结果写入临时文件，以便main.py读取
    with open('config/leftover_result.json', 'w', encoding='utf-8') as f:
        json.dump(leftover_timeslots, f)
    
    return leftover_timeslots

    