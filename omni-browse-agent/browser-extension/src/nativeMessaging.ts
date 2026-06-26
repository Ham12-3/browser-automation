export type NativeMessage = {
  request_id: string;
  tab_id: number | string | null;
  browser_name: string;
  origin: string;
  action_type: string;
  payload: Record<string, unknown>;
  timestamp: string;
};

export function sendNativeMessage(message: NativeMessage): Promise<unknown> {
  return chrome.runtime.sendNativeMessage("com.omnibrowse.agent", message);
}

