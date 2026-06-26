export type PageSnapshot = {
  title: string;
  url: string;
  visibleText: string;
  links: Array<{ text: string; href: string }>;
  buttons: Array<{ text: string; selector: string }>;
  inputs: Array<{ name: string; placeholder: string; type: string }>;
};

export function getPageSnapshot(): PageSnapshot {
  const visible = (element: Element) => {
    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.visibility !== "hidden" && style.display !== "none" && rect.width > 0 && rect.height > 0;
  };

  const links = Array.from(document.querySelectorAll<HTMLAnchorElement>("a[href]"))
    .filter(visible)
    .slice(0, 200)
    .map((link) => ({ text: link.innerText.trim(), href: link.href }));

  const buttons = Array.from(document.querySelectorAll<HTMLElement>('button,[role="button"],input[type="button"],input[type="submit"]'))
    .filter(visible)
    .slice(0, 100)
    .map((button) => ({
      text: button.innerText || button.getAttribute("value") || button.getAttribute("aria-label") || "",
      selector: button.tagName.toLowerCase()
    }));

  const inputs = Array.from(document.querySelectorAll<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>('input:not([type="password"]),textarea,select'))
    .filter(visible)
    .slice(0, 100)
    .map((input) => ({
      name: input.getAttribute("name") ?? "",
      placeholder: input.getAttribute("placeholder") ?? "",
      type: input.getAttribute("type") ?? input.tagName.toLowerCase()
    }));

  return {
    title: document.title,
    url: location.href,
    visibleText: document.body?.innerText.slice(0, 12000) ?? "",
    links,
    buttons,
    inputs
  };
}

