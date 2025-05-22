from playwright.sync_api import Page, expect
import json
import os
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator("//section//input[@id='username']")
        self.password_input = page.locator("//section//input[@id='password']")
        self.remember_me_checkbox = page.locator('//div[@class="container-ge"]//input[@type="checkbox"]')
        self.login_button = page.locator("//section//a[@id='login_submit']")
        self.yuehai_button = page.locator("div.bh-btn-primary:has-text('粤海校区')")
        self.cookie_file = os.path.join('config', 'cookies.json')
        self.storage_file = os.path.join('config', 'storage.json')

    def wait_for_page_ready(self):
        """等待页面完全加载并准备就绪"""
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_load_state('domcontentloaded')
        self.page.wait_for_load_state('load')
        return self

    def navigate(self):
        """导航到登录页面"""
        self.page.goto("https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do#/sportVenue")
        self.wait_for_page_ready()
        return self

    def save_cookies(self):
        """保存cookies和localStorage到文件"""
        self.wait_for_page_ready()
        # 等待页面上的关键元素可见，确保页面真正加载完成
        expect(self.yuehai_button).to_be_visible(timeout=5000)

        # 保存 cookies
        cookies = self.page.context.cookies()
        os.makedirs('config', exist_ok=True)
        with open(self.cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f)

        # 保存 localStorage
        storage = self.page.evaluate('''() => {
            const data = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                data[key] = localStorage.getItem(key);
            }
            return data;
        }''')
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(storage, f)
        
        return self

    def load_cookies(self):
        """从文件加载cookies和localStorage"""
        try:
            # 加载 cookies
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
                self.page.context.add_cookies(cookies)

            # 加载 localStorage
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    storage = json.load(f)
                    self.page.evaluate('''(storage) => {
                        for (const [key, value] of Object.entries(storage)) {
                            localStorage.setItem(key, value);
                        }
                    }''', storage)
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            # 检查是否存在登录后才会出现的元素（粤海校区按钮）
            return self.yuehai_button.is_visible(timeout=5000)
        except:
            return False

    def login(self, username: str, password: str):
        """执行登录操作，支持cookie登录"""
        
        if self.load_cookies():
            self.navigate()
            self.wait_for_page_ready()
            
            if self.is_logged_in():
                return self

        # Cookie登录失败，使用账号密码登录
        logger.info("can't  load cookies, try to login with username and password")
        self.navigate()
        
        # 等待登录表单元素可见
        expect(self.username_input).to_be_visible()
        expect(self.password_input).to_be_visible()
        expect(self.login_button).to_be_visible()
        
        # 执行登录操作
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.remember_me_checkbox.check()
        self.login_button.click()
        
        # 等待页面加载完成并验证登录状态
        self.wait_for_page_ready()
        
        if self.is_logged_in():
            logger.info("login success, system have saved cookies")
            self.save_cookies()
        else:
            logger.error("failed to login")
        
        return self