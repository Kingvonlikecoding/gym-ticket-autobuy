#!/usr/bin/env python3
import argparse
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright, Playwright
from utils.logger import setup_logger

from pages.login_page import LoginPage
from pages.ticket_page import TicketPage

logger = setup_logger(__name__)

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Gym Ticket Booking Script')
    parser.add_argument('--config', required=True, help='Path to config file')
    parser.add_argument('--headed', action='store_true', help='Run in headed mode')
    args = parser.parse_args()
    
    # 读取配置文件
    with open(args.config, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    # 创建Playwright实例
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=not args.headed)
        
        # 创建页面
        page = browser.new_page()
        
        try:
            # 登录
            login_page = LoginPage(page)
            login_page.login(cfg['username'], cfg['password'])

            # 预订场地
            ticket_page = TicketPage(page)
            # 使用括号 ( ... ) 可以让整个表达式自动支持换行
            if_sc=(ticket_page
                .select_campus()
                .select_venue(cfg['venue'])
                .select_date(cfg['date'], cfg['venue'], wait_timeout_seconds=float(cfg['wait_timeout_seconds']))
                .select_time_slot(cfg['time_slot'])
                .select_specific_venue(cfg['venue'], cfg.get('court'))
                .submit_booking()
                .make_payment(cfg['pay_pass'])
            )
            
            if if_sc:
                logger.info("抢票成功！")
                return 0
            
        except Exception as e:
            logger.error(f"抢票失败: {str(e)}")
            return 1
        finally:
            # 关闭浏览器
            browser.close()

if __name__ == '__main__':
    exit(main())
