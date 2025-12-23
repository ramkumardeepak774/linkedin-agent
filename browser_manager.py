import asyncio
import os
import json
import random
from pathlib import Path
from playwright.async_api import async_playwright
from config import Config

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.cookies_path = Config.DATA_DIR / "linkedin_cookies.json"

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=Config.HEADLESS,
            slow_mo=50  # Human-like speed
        )
        
        # Load cookies if they exist
        if self.cookies_path.exists():
            print("Loading cookies from cache...")
            with open(self.cookies_path, 'r') as f:
                cookies = json.load(f)
            
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            await self.context.add_cookies(cookies)
        else:
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            
        self.page = await self.context.new_page()
        print("Browser Started.")

    async def close(self):
        if self.context:
            # Save cookies before closing
            cookies = await self.context.cookies()
            with open(self.cookies_path, 'w') as f:
                json.dump(cookies, f)
            print("Cookies saved.")
            
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("Browser Closed.")
    
    async def type_human(self, selector, text):
        """Types text with random delays to mimic human behavior."""
        await self.page.focus(selector)
        for char in text:
            await self.page.keyboard.type(char)
            # Random delay between keystrokes
            await asyncio.sleep(random.uniform(0.05, 0.2))

    async def login(self):
        if not self.page:
            await self.start()
            
        print("Navigating to LinkedIn...")
        await self.page.goto("https://www.linkedin.com/login")
        await self.page.wait_for_timeout(2000)

        # Check if already logged in (by looking for common logged-in elements)
        # Or if the URL redirected to feed
        if "feed" in self.page.url or await self.page.query_selector(".global-nav__content"):
            print("Already logged in via cookies!")
            return True

        # Need to login
        print("Logging in with credentials...")
        if not Config.LINKEDIN_USERNAME or not Config.LINKEDIN_PASSWORD:
            print("ERROR: Credentials not found in config/env!")
            return False

        try:
            await self.type_human("#username", Config.LINKEDIN_USERNAME)
            await self.page.wait_for_timeout(500)
            await self.type_human("#password", Config.LINKEDIN_PASSWORD)
            await self.page.wait_for_timeout(1000)
            
            await self.page.click("button[type='submit']")
            print("Submitted credentials.")
            
            # Wait for navigation - MANUAL INTERVENTION MIGHT BE NEEDED (2FA)
            # We give a generous timeout for the user to handle 2FA if needed
            print("Waiting for login to complete... (If 2FA is asked, please handle it in the browser window)")
            try:
                await self.page.wait_for_selector(".global-nav__content", state="visible", timeout=60000) # 60s timeout
                print("Login Successful!")
                return True
            except:
                print("Login timed out. Did 2FA fail?")
                return False
                
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    async def search_jobs(self, query="Software Engineer", location="United States"):
        """
        Searches for jobs and returns a list of job objects.
        """
        if not self.page:
            await self.login()
            
        print(f"Searching for '{query}' in '{location}'...")
        # Construct URL
        # We use 'f_AL=true' for Easy Apply if we want (optional, maybe later)
        url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}"
        await self.page.goto(url)
        await self.page.wait_for_timeout(3000)
        
        # Scroll to load a few items
        for _ in range(3):
            await self.page.keyboard.press("PageDown")
            await self.page.wait_for_timeout(1000)
            
        print("Extracting job listings...")
        # Select all job cards
        job_cards = await self.page.query_selector_all(".job-card-container")
        
        jobs = []
        for card in job_cards:
            try:
                # Extract Title - Updated selectors for current LinkedIn
                title_el = await card.query_selector("a.job-card-container__link strong")
                if not title_el:
                    title_el = await card.query_selector(".job-card-list__title strong")
                title = await title_el.inner_text() if title_el else "Unknown"
                
                # Extract ID
                job_id = await card.get_attribute("data-job-id")
                
                # Extract Company - Updated selector
                company_el = await card.query_selector(".artdeco-entity-lockup__subtitle")
                if not company_el:
                    company_el = await card.query_selector(".job-card-container__primary-description")
                company = await company_el.inner_text() if company_el else "Unknown"
                
                # Extract Link
                link_el = await card.query_selector("a.job-card-container__link")
                if not link_el:
                    link_el = await card.query_selector("a.job-card-list__title")
                link = await link_el.get_attribute("href") if link_el else ""
                
                if job_id:
                    jobs.append({
                        "id": job_id,
                        "title": title.strip().replace("\n", " "),
                        "company": company.strip().replace("\n", " "),
                        "url": f"https://www.linkedin.com{link}" if link.startswith("/") else link
                    })
            except Exception as e:
                # Ignore bad cards
                print(f"Skipping card due to error: {e}")
                continue
                
        print(f"Found {len(jobs)} jobs.")
        return jobs

    async def goto_linkedin(self):
        # Renamed/Deprecated logic, just calls login
        await self.login()

if __name__ == "__main__":
    async def test():
        bm = BrowserManager()
        await bm.login()
        await asyncio.sleep(5)
        await bm.close()
    
    asyncio.run(test())
