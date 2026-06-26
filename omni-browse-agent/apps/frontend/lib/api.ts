const API_BASE = process.env.NEXT_PUBLIC_OMNI_API_BASE ?? "http://127.0.0.1:8765";

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}

export type BrowserInfo = {
  browser_name: string;
  process_name?: string | null;
  window_title?: string | null;
  cdp_available: boolean;
  extension_available: boolean;
  accessibility_available: boolean;
  visual_fallback_available: boolean;
  endpoint_url?: string | null;
  tabs: Array<{ title?: string; url?: string }>;
};

