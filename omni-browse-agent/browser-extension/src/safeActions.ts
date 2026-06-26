const RESTRICTED_PROTOCOLS = ["chrome:", "edge:", "brave:", "about:", "moz-extension:", "chrome-extension:"];

export function isRestrictedPage(url: string): boolean {
  return RESTRICTED_PROTOCOLS.some((protocol) => url.startsWith(protocol));
}

export function redactSensitiveText(actionType: string, value: string): string {
  if (actionType.toLowerCase().includes("password")) {
    return "[REDACTED]";
  }
  return value;
}

