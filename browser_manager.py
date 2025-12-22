import asyncio
from playwright.async_api import async_playwright
from config import Config

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=Config.HEADLESS,
            slow_mo=50  # Human-like speed
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        self.page = await self.context.new_page()
        print("Browser Started.")

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("Browser Closed.")

    async def goto_linkedin(self):
        if not self.page:
            await self.start()
        await self.page.goto("https://www.linkedin.com")
        await self.page.wait_for_timeout(2000)

if __name__ == "__main__":
    async def test():
        bm = BrowserManager()
        await bm.start()
        await bm.goto_linkedin()
        await asyncio.sleep(5)
        await bm.close()
    
    asyncio.run(test())
