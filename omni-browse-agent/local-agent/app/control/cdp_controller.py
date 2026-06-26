import asyncio
from typing import Any

from playwright.async_api import Browser, Page, async_playwright

from app.control.base import BrowserController


class CdpController(BrowserController):
    mode_name = "cdp"

    def __init__(self, endpoint_url: str) -> None:
        self.endpoint_url = endpoint_url
        self._playwright: Any = None
        self._browser: Browser | None = None
        self._page: Page | None = None
        self._stopped = False

    async def connect(self) -> None:
        if self._browser:
            return
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.connect_over_cdp(self.endpoint_url)
        self._page = await self._select_active_page()

    async def _select_active_page(self) -> Page:
        assert self._browser is not None
        for context in self._browser.contexts:
            pages = context.pages
            if pages:
                return pages[-1]
        context = self._browser.contexts[0] if self._browser.contexts else await self._browser.new_context()
        return await context.new_page()

    async def _page_or_connect(self) -> Page:
        await self.connect()
        assert self._page is not None
        return self._page

    async def observe(self) -> dict[str, Any]:
        page = await self._page_or_connect()
        try:
            visible_text = await page.locator("body").inner_text(timeout=3000)
        except Exception:
            visible_text = ""
        data = await page.evaluate(
            """() => {
                const visible = (el) => {
                  const style = window.getComputedStyle(el);
                  const rect = el.getBoundingClientRect();
                  return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
                };
                const map = (selector, mapper) => Array.from(document.querySelectorAll(selector)).filter(visible).slice(0, 200).map(mapper);
                return {
                  title: document.title,
                  url: location.href,
                  links: map('a[href]', a => ({text: a.innerText.trim(), href: a.href})),
                  buttons: map('button,[role="button"],input[type=button],input[type=submit]', b => ({text: b.innerText || b.value || b.getAttribute('aria-label') || '', selector: b.tagName.toLowerCase()})),
                  inputs: map('input:not([type=password]),textarea,select', i => ({name: i.name || '', placeholder: i.placeholder || '', type: i.type || i.tagName.toLowerCase()})),
                  headings: map('h1,h2,h3', h => ({level: h.tagName.toLowerCase(), text: h.innerText.trim()})),
                  iframes: Array.from(document.querySelectorAll('iframe')).map(i => i.src || ''),
                  scripts: Array.from(document.querySelectorAll('script[src]')).map(s => s.src || '')
                };
            }"""
        )
        data["visible_text"] = visible_text[:12000]
        return data

    async def navigate(self, url: str) -> dict[str, Any]:
        page = await self._page_or_connect()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return await self.observe()

    async def click(self, target: dict[str, Any]) -> dict[str, Any]:
        page = await self._page_or_connect()
        locator = self._locator_from_target(page, target)
        await locator.first.click(timeout=7000)
        return await self.observe()

    async def type(self, target: dict[str, Any], text: str) -> dict[str, Any]:
        page = await self._page_or_connect()
        locator = self._locator_from_target(page, target)
        await locator.first.fill(text, timeout=7000)
        return await self.observe()

    async def press(self, key: str) -> dict[str, Any]:
        page = await self._page_or_connect()
        await page.keyboard.press(key)
        return await self.observe()

    async def scroll(self, direction: str, amount: int) -> dict[str, Any]:
        page = await self._page_or_connect()
        delta = amount if direction.lower() in {"down", "right"} else -amount
        await page.mouse.wheel(0, delta)
        return await self.observe()

    async def extract(self, schema: dict[str, Any]) -> dict[str, Any]:
        page = await self._page_or_connect()
        name = schema.get("name")
        if name == "hacker_news_top":
            items = await page.evaluate(
                """() => Array.from(document.querySelectorAll('tr.athing')).slice(0, 10).map(row => {
                    const link = row.querySelector('.titleline a');
                    const subtext = row.nextElementSibling;
                    return {
                      title: link ? link.textContent.trim() : '',
                      url: link ? link.href : '',
                      rank: Number((row.querySelector('.rank')?.textContent || '').replace('.', '')) || null,
                      score: subtext?.querySelector('.score')?.textContent || null,
                      comments: subtext?.querySelector('a:last-child')?.textContent || null
                    };
                })"""
            )
            return {"schema": name, "data": items}
        links = await page.evaluate(
            """() => Array.from(document.querySelectorAll('a[href]')).slice(0, 100).map(a => ({title: a.innerText.trim(), url: a.href}))"""
        )
        return {"schema": name or "links", "data": links}

    async def screenshot(self) -> bytes:
        page = await self._page_or_connect()
        return await page.screenshot(full_page=False)

    async def wait(self, condition: dict[str, Any]) -> dict[str, Any]:
        page = await self._page_or_connect()
        if selector := condition.get("selector"):
            await page.wait_for_selector(selector, timeout=int(condition.get("timeout_ms", 10000)))
        else:
            await asyncio.sleep(float(condition.get("seconds", 1)))
        return await self.observe()

    async def stop(self) -> None:
        self._stopped = True

    async def resume(self) -> None:
        self._stopped = False

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._playwright = None
        self._page = None

    def _locator_from_target(self, page: Page, target: dict[str, Any]):
        kind = target.get("kind", "selector")
        value = target.get("value", "")
        if kind == "selector":
            return page.locator(value)
        if kind == "text":
            return page.get_by_text(value, exact=False)
        if kind == "role":
            return page.get_by_role(target.get("role", "button"), name=value)
        raise ValueError(f"Unsupported target kind: {kind}")
