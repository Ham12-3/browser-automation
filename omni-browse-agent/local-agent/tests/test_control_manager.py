import pytest

from app.control.manager import BrowserControlManager


@pytest.mark.asyncio
async def test_detect_browsers_returns_list_without_cdp() -> None:
    browsers = await BrowserControlManager().detect_browsers()

    assert isinstance(browsers, list)

