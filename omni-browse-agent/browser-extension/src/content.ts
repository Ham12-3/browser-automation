import { getPageSnapshot } from "./pageSnapshot";
import { isRestrictedPage } from "./safeActions";

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (isRestrictedPage(location.href)) {
    sendResponse({ ok: false, error: "Restricted browser page" });
    return true;
  }

  if (message?.type === "getPageSnapshot") {
    sendResponse({ ok: true, snapshot: getPageSnapshot() });
    return true;
  }

  sendResponse({ ok: false, error: "Unknown action" });
  return true;
});

