from dataclasses import dataclass
from typing import Any


CAPTCHA_SIGNALS = (
    "recaptcha",
    "hcaptcha",
    "turnstile",
    "captcha",
    "i am not a robot",
    "verify you are human",
    "cloudflare challenge",
    "cf-challenge",
)


@dataclass(frozen=True)
class CaptchaDetection:
    detected: bool
    reason: str | None = None
    signals: list[str] | None = None


class CaptchaDetector:
    def detect(self, observation: dict[str, Any]) -> CaptchaDetection:
        parts: list[str] = []
        for key in ("url", "title", "visible_text", "dom_text"):
            value = observation.get(key)
            if isinstance(value, str):
                parts.append(value)

        for collection_key in ("iframes", "scripts", "elements"):
            collection = observation.get(collection_key)
            if isinstance(collection, list):
                parts.extend(str(item) for item in collection)

        haystack = "\n".join(parts).lower()
        matches = [signal for signal in CAPTCHA_SIGNALS if signal in haystack]
        if matches:
            return CaptchaDetection(
                detected=True,
                reason="CAPTCHA detected. Please complete it manually.",
                signals=matches,
            )
        return CaptchaDetection(detected=False, signals=[])

