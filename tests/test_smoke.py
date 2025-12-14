#!/usr/bin/env python3
import pytest
import sys
import os
from datetime import date, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接使用utils.logger，它会自动检测测试环境
from utils.logger import setup_logger

from pages.login_page import LoginPage
from pages.ticket_page import TicketPage

logger = setup_logger(__name__)

def test_main_flow_success(page, test_config):
    """测试完整主流程成功执行"""
    # 登录
    login_page = LoginPage(page)
    login_page.login(test_config['username'], test_config['password'])

    # 预订场地
    ticket_page = TicketPage(page)
    (ticket_page
        .select_campus()
        .select_venue(test_config['venue'])
        .select_date(test_config['date'], test_config['venue'], wait_timeout_seconds=float(test_config['wait_timeout_seconds']))
        .select_time_slot(test_config['time_slot'])
        .select_specific_venue(test_config['venue'], test_config.get('court'))
        .submit_booking()
        # 实际支付可能需要真实支付环境，这里仅验证到提交预订步骤
    )
    
    logger.info("test_main_flow_success completed successfully")
    logger.info("主流程测试成功！")
