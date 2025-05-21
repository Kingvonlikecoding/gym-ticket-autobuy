from playwright.sync_api import Page, TimeoutError
import random
from datetime import date, timedelta
from utils.logger import setup_logger
from pages.pay_page import PayPage

logger = setup_logger(__name__)

class TicketPage:
    def __init__(self, page: Page):
        self.page = page
        self.venue_images = {
            'A': '6cf6b63b970a4f4b87193d799d8092c7',  # 健身房
            'B': '317a6df934914473b49996840b305987',  # 羽毛球
            'C': 'eaaf3fd0bf624a328966f987fcd0ac52'   # 篮球
        }

    def select_campus(self):
        """选择粤海校区"""
        self.page.click("div.bh-btn-primary:has-text('粤海校区')")
        return self

    def select_venue(self, venue_type: str):
        """选择场馆"""
        image_id = self.venue_images.get(venue_type)
        if not image_id:
            raise ValueError(f"Unsupported venue type: {venue_type}")
        
        self.page.wait_for_selector(f"img.union-2[src*='{image_id}']", timeout=10000)
        self.page.click(f"img.union-2[src*='{image_id}']")
        return self

    def select_date(self, da_te: str, max_attempts=10, wait_timeout_seconds=10):
        """选择日期（今天或明天）"""
        today = date.today().strftime("%Y-%m-%d")
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        if da_te=='today':
            da_te = today
        else:
            da_te = tomorrow
        target_selector = f"//label/div[contains(.,'{da_te}')]"

        for attempt in range(max_attempts):
            if attempt > 0:
                self.page.reload()
                self.select_campus()
                self.select_venue(self.current_venue_type)

            try:
                date_locator = self.page.locator(target_selector)
                date_locator.wait_for(state='visible', timeout=wait_timeout_seconds * 1000)
                date_locator.click()
                return self
            except TimeoutError:
                if attempt >= max_attempts - 1:
                    raise RuntimeError(f"时间未到或没票了: Failed to find and click date '{da_te}' after {max_attempts} attempts.")
        return self

    def select_time_slot(self, time_slot: str):
        """选择时间段"""
        self.page.click(f"div.element:has-text('{time_slot}')")
        return self

    def select_specific_venue(self, venue_type: str, court=None):
        """选择具体场地"""
        self.current_venue_type = venue_type
        if venue_type == 'A':   # 健身房
            self.page.wait_for_selector("div.element:has-text('一楼健身房(')", timeout=10000)
            self.page.click("div.element:has-text('一楼健身房(')")
        elif venue_type == 'B':  # 羽毛球
            available_venues = self.page.locator("div.element:has-text('可预约')").all()
            visible_venues = [v for v in available_venues if v.is_visible()]
            if not visible_venues:
                raise RuntimeError("无体育场馆了")
            chosen_venue = random.choice(visible_venues)
            logger.info(f"随机选择场地: '{chosen_venue.text_content()}'")
            chosen_venue.click()
        elif venue_type == 'C': # 篮球
            self.page.wait_for_selector("div.element:has-text('号场(')", timeout=10000)
            if court == 'out':
                self.page.click("div.element:has-text('天台篮球4号场')")
            else:
                self.page.click("div.element:has-text('东馆篮球3号场')")
        return self

    def submit_booking(self):
        """提交预约"""
        self.page.click("button.bh-btn.bh-btn-default.bh-btn-large:has-text('提交预约')")
        return self

    def make_payment(self,pay_password):
        """支付订单"""
        self.page.click("a:has-text('未支付')")
        self.page.wait_for_selector("button:has-text(')支付')", timeout=10000)
        payments = [p for p in self.page.get_by_text(')支付').all() if p.is_visible()]
        if len(payments) == 1:
            self.page.click("button:has-text('(剩余金额)支付')")
        else:
            # 使用 PayPage 完成支付流程
            pay_page = PayPage(self.page)
            (pay_page 
                .pay_with_sports_fund() 
                .click_next_step() 
                .enter_password(pay_password)
            )

        return self

    def verify_payment_success(self):
        """验证支付成功"""
        self.page.get_by_text('支付成功').wait_for(state='visible')
        logger.info("✅ 支付成功!")
        return self