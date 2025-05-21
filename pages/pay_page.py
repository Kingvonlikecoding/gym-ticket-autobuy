from playwright.sync_api import Page

class PayPage:
    def __init__(self, page: Page):
        self.page = page

    def pay_with_sports_fund(self):
        """使用体育经费支付，并切换到新标签页"""
        with self.page.expect_popup() as page1:
            self.page.click("button:has-text('(体育经费)支付')")
        self.page = page1.value  # 将当前 page 替换为新标签页
        return self

    def click_next_step(self):
        """点击下一步"""
        self.page.wait_for_selector("button:has-text('下一步')", timeout=10000)
        self.page.click("button:has-text('下一步')")
        return self

    def enter_password(self, password: str):
        """输入支付密码"""
        self.page.wait_for_selector("input#password", timeout=10000)
        self.page.click("input#password")

        for digit in password:
            self.page.locator(f".key-{digit}").click()
        
        self.page.locator(".next-button-max").click()
        return self