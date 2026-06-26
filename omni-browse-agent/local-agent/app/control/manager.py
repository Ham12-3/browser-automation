import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any

import httpx

from app.control.accessibility_controller import AccessibilityController
from app.control.base import BrowserController
from app.control.cdp_controller import CdpController
from app.control.extension_controller import ExtensionController
from app.control.visual_controller import VisualController
from app.desktop.window_detector import detect_browser_processes
from app.schemas import BrowserInfo
from app.utils.errors import ControlModeUnavailable


CDP_PORTS = (9222, 9223, 9224, 9225)


class BrowserControlManager:
    def __init__(self) -> None:
        self.selected_browser: BrowserInfo | None = None
        self.controller: BrowserController | None = None

    async def detect_browsers(self) -> list[BrowserInfo]:
        cdp_browsers = await self._detect_cdp_browsers()
        process_browsers = detect_browser_processes()
        by_name: dict[str, BrowserInfo] = {f"{b.browser_name}:{b.endpoint_url}": b for b in cdp_browsers}
        for browser in process_browsers:
            key = f"{browser.browser_name}:{browser.window_title or browser.process_name}"
            if key not in by_name:
                by_name[key] = browser
        return list(by_name.values())

    async def select_best(self) -> BrowserController:
        browsers = await self.detect_browsers()
        cdp = next((browser for browser in browsers if browser.cdp_available and browser.endpoint_url), None)
        if not cdp:
            cdp = await self._try_start_chrome_cdp()
        if cdp:
            self.selected_browser = cdp
            self.controller = CdpController(cdp.endpoint_url or "")
            return self.controller
        extension = next((browser for browser in browsers if browser.extension_available), None)
        if extension:
            self.selected_browser = extension
            self.controller = ExtensionController()
            return self.controller
        raise ControlModeUnavailable(
            "No executable browser control mode is available. Chrome CDP could not be reached or started on http://127.0.0.1:9222."
        )

    async def get_controller(self) -> BrowserController:
        if self.controller:
            return self.controller
        return await self.select_best()

    async def observe(self) -> dict[str, Any]:
        return await (await self.get_controller()).observe()

    async def navigate(self, url: str) -> dict[str, Any]:
        return await (await self.get_controller()).navigate(url)

    async def click(self, target: dict[str, Any]) -> dict[str, Any]:
        return await (await self.get_controller()).click(target)

    async def type(self, target: dict[str, Any], text: str) -> dict[str, Any]:
        return await (await self.get_controller()).type(target, text)

    async def press(self, key: str) -> dict[str, Any]:
        return await (await self.get_controller()).press(key)

    async def scroll(self, direction: str, amount: int) -> dict[str, Any]:
        return await (await self.get_controller()).scroll(direction, amount)

    async def extract(self, schema: dict[str, Any]) -> dict[str, Any]:
        return await (await self.get_controller()).extract(schema)

    async def screenshot(self) -> bytes:
        return await (await self.get_controller()).screenshot()

    async def wait(self, condition: dict[str, Any]) -> dict[str, Any]:
        return await (await self.get_controller()).wait(condition)

    async def stop(self) -> None:
        if self.controller:
            await self.controller.stop()

    async def resume(self) -> None:
        if self.controller:
            await self.controller.resume()

    async def _detect_cdp_browsers(self) -> list[BrowserInfo]:
        async with httpx.AsyncClient(timeout=0.4) as client:
            tasks = [self._probe_cdp(client, port) for port in CDP_PORTS]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        return [result for result in results if isinstance(result, BrowserInfo)]

    async def _probe_cdp(self, client: httpx.AsyncClient, port: int) -> BrowserInfo | None:
        base = f"http://127.0.0.1:{port}"
        try:
            version = (await client.get(f"{base}/json/version")).json()
            tabs = (await client.get(f"{base}/json/list")).json()
        except Exception:
            return None
        browser_value = str(version.get("Browser", "Chromium")).split("/")[0]
        return BrowserInfo(
            browser_name=browser_value,
            process_name=None,
            cdp_available=True,
            endpoint_url=base,
            tabs=[
                {"id": tab.get("id"), "title": tab.get("title"), "url": tab.get("url"), "type": tab.get("type")}
                for tab in tabs
                if tab.get("type") == "page"
            ],
        )

    async def _try_start_chrome_cdp(self) -> BrowserInfo | None:
        if os.name != "nt":
            return None
        chrome = self._find_chrome_path()
        if not chrome:
            return None

        profile = Path(os.environ.get("TEMP", ".")) / "omnibrowse-chrome-cdp"
        subprocess.Popen(
            [
                str(chrome),
                "--remote-debugging-port=9222",
                f"--user-data-dir={profile}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        for _ in range(12):
            await asyncio.sleep(0.5)
            browsers = await self._detect_cdp_browsers()
            cdp = next((browser for browser in browsers if browser.cdp_available and browser.endpoint_url), None)
            if cdp:
                return cdp
        return None

    def _find_chrome_path(self) -> Path | None:
        candidates = [
            Path(os.environ.get("PROGRAMFILES", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        ]
        return next((path for path in candidates if path.exists()), None)
