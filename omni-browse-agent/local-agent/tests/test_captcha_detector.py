from app.safety.captcha_detector import CaptchaDetector


def test_detects_recaptcha_iframe() -> None:
    detection = CaptchaDetector().detect(
        {
            "url": "https://example.com",
            "iframes": ["https://www.google.com/recaptcha/api2/anchor"],
            "visible_text": "",
        }
    )

    assert detection.detected is True
    assert "recaptcha" in (detection.signals or [])


def test_detects_verify_you_are_human_text() -> None:
    detection = CaptchaDetector().detect({"visible_text": "Please verify you are human before continuing."})

    assert detection.detected is True


def test_ignores_normal_pages() -> None:
    detection = CaptchaDetector().detect({"visible_text": "Top stories and links", "title": "Hacker News"})

    assert detection.detected is False

