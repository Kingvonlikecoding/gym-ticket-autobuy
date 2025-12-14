import pytest
import json
import os
import sys
from playwright.sync_api import sync_playwright, Playwright

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入项目通用日志器
from utils.logger import setup_logger

# 配置logger
logger = setup_logger(__name__)

@pytest.fixture(scope="session")
def playwright_instance():
    """提供Playwright实例"""
    with sync_playwright() as playwright:
        yield playwright

@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, pytestconfig):
    """提供浏览器实例，支持从命令行接收--headed参数"""
    # 检查是否有--headed参数，如果有则使用headless=False
    headless = not pytestconfig.getoption("headed")
    
    browser = playwright_instance.chromium.launch(
        headless=headless,  # 根据命令行参数决定是否使用无头模式
        slow_mo=500         # 慢速执行，便于观察
    )
    yield browser
    browser.close()

@pytest.fixture(scope="session")
def context(browser):
    """提供浏览器上下文"""
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture(scope="session")
def page(context):
    """提供浏览器页面"""
    page = context.new_page()
    yield page
    page.close()

@pytest.fixture(scope="session")
def test_config():
    """提供测试配置"""
    # 默认测试配置
    config = {
        "username": "test_user",
        "password": "test_password",
        "target_url": "https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do",  # 实际的目标URL
        "venue": "A",
        "date": "today",
        "time_slot": "14:00-16:00",
        "wait_timeout_seconds": 10,
        "pay_pass": "",
        "court": "out"
    }
    
    # 如果存在测试配置文件，加载它
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config.update(json.load(f))
    
    yield config

@pytest.fixture(scope="function")
def reset_page(page):
    """重置页面状态"""
    page.goto("about:blank")
    yield page

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """pytest配置"""
    # 设置日志级别
    if config.getoption("verbose"):
        import logging
        logging.basicConfig(level=logging.INFO)
    
    # 创建测试结果目录
    os.makedirs("test_results", exist_ok=True)

@pytest.hookimpl(tryfirst=True)
def pytest_report_header(config):
    """测试报告头部"""
    return [
        "Gym Ticket Autobuy Test Suite",
        "Author: Trae AI",
        "Date: 2025-12-14"
    ]