import { sendNativeMessage } from "./nativeMessaging";

chrome.runtime.onInstalled.addListener(() => {
  chrome.action.setBadgeText({ text: "OFF" });
});

chrome.action.onClicked.addListener(async (tab) => {
  chrome.action.setBadgeText({ text: "ON", tabId: tab.id });
  await sendNativeMessage({
    request_id: crypto.randomUUID(),
    tab_id: tab.id ?? null,
    browser_name: "chromium",
    origin: tab.url ?? "",
    action_type: "getActiveTab",
    payload: { title: tab.title, url: tab.url },
    timestamp: new Date().toISOString()
  });
});

