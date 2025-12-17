from playwright.sync_api import Page, TimeoutError
import random
from datetime import date, timedelta
from pages.pay_page import PayPage

# 直接使用utils.logger，它会自动检测测试环境
from utils.logger import setup_logger

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
            logger.error(f"Unsupported venue type: {venue_type}, it should be one of [A, B, C]")
            raise ValueError(f"Unsupported venue type: {venue_type}")
        
        self.page.wait_for_selector(f"img.union-2[src*='{image_id}']", timeout=10000)
        self.page.click(f"img.union-2[src*='{image_id}']")
        return self

    def select_date(self, da_te: str, venue_type: str, wait_timeout_seconds: float, max_attempts=100):
        """选择日期（今天或明天）"""
        today = date.today().strftime("%Y-%m-%d")
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        dajiba= (date.today() + timedelta(days=2)).strftime("%Y-%m-%d") # 用来测试
        if da_te=='today':
            da_te = today
        elif da_te=='tomorrow':
            da_te = tomorrow
        else:
            da_te = dajiba
        target_selector = f"//label/div[contains(.,'{da_te}')]"
        logger.info(f"Selecting date: {da_te}")

        for attempt in range(max_attempts):
            if attempt > 0:
                self.page.reload()
                self.page.wait_for_load_state('networkidle')
                self.page.wait_for_load_state('domcontentloaded')
                self.page.wait_for_load_state('load')
                self.select_campus()
                self.select_venue(venue_type)

            try:
                date_locator = self.page.locator(target_selector)
                date_locator.wait_for(state='visible', timeout=wait_timeout_seconds * 1000)
                date_locator.click()
                return self
            except TimeoutError:
                if attempt >= max_attempts - 1:
                    logger.info(f"Failed to find date '{da_te}' after {max_attempts} attempts.")
                    raise RuntimeError(f"Failed to find and click date '{da_te}' after {max_attempts} attempts.")
                else: 
                    logger.info(f"Failed to find date '{da_te}' , retrying...")
        return self

    def select_time_slot(self, time_slot: str):
        """选择时间段"""
        try:
            self.page.click(f"div.element:has-text('{time_slot}')")
        except TimeoutError:
            logger.error(f"Failed to select time slot: {time_slot}")
        return self

    def leftover_timeslot(self):
        """查询当日有票的时间段"""
        self.page.wait_for_timeout(300)
        available_timeslots = self.page.locator("div.element:has-text('可预约')").all()
        visible_timeslots = [t for t in available_timeslots if t.is_visible()]
        if not visible_timeslots:
            logger.error("no timeslots available")
            return None
        # 返回时间段的文本内容，而不是Locator对象
        return [t.text_content().strip() for t in visible_timeslots]

    def select_specific_venue(self, venue_type: str, court=None):
        """选择具体场地"""
        self.current_venue_type = venue_type
        if venue_type == 'A':   # 健身房
            try:
                self.page.wait_for_selector("div.element:has-text('一楼健身房(')", timeout=10000)
                self.page.click("div.element:has-text('一楼健身房(')")
                logger.info("Selected gym venue: 一楼健身房")
            except TimeoutError:
                logger.error("no gym venue available")
                raise RuntimeError("no gym venue available")
        elif venue_type == 'B':  # 羽毛球
            available_venues = self.page.locator("//label/div[contains(.,'可预约') and contains(.,'羽毛球场')]").all()
            visible_venues = [v for v in available_venues if v.is_visible()]
            if not visible_venues:
                logger.error("no venues available in the timeslot")
                raise RuntimeError("无体育场馆了")
            chosen_venue = random.choice(visible_venues)
            logger.info(f"随机选择场地: '{chosen_venue.text_content()}'")
            chosen_venue.click()
            logger.info(f"Selected badminton venue: {chosen_venue.text_content()}")
        elif venue_type == 'C': # 篮球
            self.page.wait_for_selector("div.element:has-text('号场(')", timeout=10000)
            if court == 'out':
                self.page.click("div.element:has-text('天台篮球4号场')")
                logger.info("Selected basketball venue: 天台篮球4号场")
            else:
                self.page.click("div.element:has-text('东馆篮球3号场')")
                logger.info("Selected basketball venue: 东馆篮球3号场")
        return self

    def submit_booking(self):
        """提交预约"""
        self.page.click("button.bh-btn.bh-btn-default.bh-btn-large:has-text('提交预约')")
        logger.info("Submitted booking")
        return self

    def make_payment(self,pay_password):
        """支付订单"""
        self.page.click("a:has-text('未支付')")
        self.page.wait_for_selector("button:has-text(')支付')", timeout=10000)
        payments = [p for p in self.page.get_by_text(')支付').all() if p.is_visible()]
        if len(payments) == 1:
            self.page.click("button:has-text('(剩余金额)支付')")
            logger.info("buy ticket success!!! 买票成功 !!!")
        else:
            # 使用 PayPage 完成支付流程
            pay_page = PayPage(self.page)
            (pay_page 
                .pay_with_sports_fund() 
                .click_next_step() 
                .enter_password(pay_password)
            )
            return True

        return self
