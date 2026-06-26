from app.safety.policy_checker import PolicyChecker
from app.schemas import AgentAction


def test_allows_low_risk_navigation() -> None:
    result = PolicyChecker().check(
        AgentAction(
            type="navigate",
            payload={"url": "https://news.ycombinator.com/"},
            reason="Open Hacker News",
            risk_level="low",
        )
    )

    assert result.allowed is True
    assert result.requires_approval is False
    assert result.risk_level == "low"


def test_blocks_captcha_bypass_request() -> None:
    result = PolicyChecker().check(
        AgentAction(
            type="click",
            target={"kind": "text", "value": "captcha"},
            reason="bypass captcha challenge",
            risk_level="low",
        )
    )

    assert result.allowed is False
    assert result.risk_level == "blocked"


def test_requires_approval_for_password_typing() -> None:
    result = PolicyChecker().check(
        AgentAction(
            type="type",
            target={"kind": "selector", "value": "input[name=password]"},
            payload={"text": "secret"},
            reason="type password",
            risk_level="high",
        )
    )

    assert result.allowed is True
    assert result.requires_approval is True
    assert result.risk_level == "high"

