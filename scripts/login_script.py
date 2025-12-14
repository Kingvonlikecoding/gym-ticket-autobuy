#!/usr/bin/env python3
import argparse
import json
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright, Playwright
from utils.logger import setup_logger
from pages.login_page import LoginPage

logger = setup_logger(__name__)

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Gym Login Script')
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
            if login_page.login(cfg['username'], cfg['password']):
                # 登录成功，保持浏览器打开
                try:
                    while True:
                        time.sleep(1)
                        page.title()
                except Exception as e:
                    logger.info(f"浏览器已关闭: {str(e)}")
            else:
                # 登录失败
                logger.error("登录失败")
                return 1
                
            return 0
            
        except Exception as e:
            logger.error(f"登录过程中发生错误: {str(e)}")
            return 1
        finally:
            # 关闭浏览器
            browser.close()

if __name__ == '__main__':
    exit(main())
