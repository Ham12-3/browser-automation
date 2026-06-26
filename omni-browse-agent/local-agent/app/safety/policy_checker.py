from urllib.parse import urlparse

from app.config import Settings, get_settings
from app.schemas import AgentAction, PolicyResult


BLOCKED_KEYWORDS = (
    "captcha solving",
    "captcha bypass",
    "bypass captcha",
    "anti-bot",
    "stealth",
    "proxy rotation",
    "fingerprint spoof",
    "credential theft",
    "steal password",
    "bypass login",
)

HIGH_RISK_ACTIONS = {"type", "press", "click"}
HIGH_RISK_KEYWORDS = (
    "password",
    "payment",
    "credit card",
    "delete account",
    "purchase",
    "buy",
    "send message",
    "post comment",
    "submit",
    "upload",
    "download",
    "accept terms",
    "grant permission",
    "login",
    "log in",
)


class PolicyChecker:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def check(self, action: AgentAction, *, current_url: str | None = None, visible_text: str | None = None) -> PolicyResult:
        haystack = " ".join(
            part.lower()
            for part in [
                action.reason,
                action.type,
                action.target.value if action.target else "",
                str(action.payload),
                current_url or "",
                visible_text or "",
            ]
        )

        if any(keyword in haystack for keyword in BLOCKED_KEYWORDS):
            return PolicyResult(
                allowed=False,
                requires_approval=False,
                reason="Blocked by safety policy: CAPTCHA bypass, stealth, credential theft, or access-control bypass is not allowed.",
                risk_level="blocked",
            )

        url = action.payload.get("url") if action.type == "navigate" else current_url
        if isinstance(url, str) and self._is_blocked_domain(url):
            return PolicyResult(
                allowed=False,
                requires_approval=False,
                reason=f"Blocked domain: {urlparse(url).netloc}",
                risk_level="blocked",
            )

        if action.risk_level == "high" or any(keyword in haystack for keyword in HIGH_RISK_KEYWORDS):
            return PolicyResult(
                allowed=True,
                requires_approval=True,
                reason="High-risk browser action requires human approval.",
                risk_level="high",
            )

        if action.risk_level == "medium":
            return PolicyResult(
                allowed=True,
                requires_approval=True,
                reason="Medium-risk action requires approval in this local-first MVP.",
                risk_level="medium",
            )

        return PolicyResult(
            allowed=True,
            requires_approval=False,
            reason="Low risk browser action.",
            risk_level="low",
        )

    def _is_blocked_domain(self, url: str) -> bool:
        hostname = urlparse(url).hostname or ""
        return any(hostname == domain or hostname.endswith(f".{domain}") for domain in self.settings.blocked_domains)

