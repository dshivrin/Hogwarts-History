from __future__ import annotations

import hashlib

from scripts.fanfic_dataset.policy import evaluate_policy


def test_policy_raises_effective_delay_to_robots_value():
    robots = "User-agent: *\nAllow: /\nCrawl-delay: 5\n"
    decision = evaluate_policy("https://www.fanfiction.net/s/1/1/x", robots, 3.0)
    assert decision.allowed is True
    assert decision.effective_delay_seconds == 5.0


def test_policy_rejects_disallowed_story_path():
    robots = "User-agent: *\nDisallow: /s/\n"
    decision = evaluate_policy("https://www.fanfiction.net/s/1/1/x", robots, 5.0)
    assert decision.allowed is False


def test_policy_enforces_floor_and_records_exact_robots_snapshot() -> None:
    robots = "User-agent: *\r\nAllow: /\r\n"
    decision = evaluate_policy("https://www.fanfiction.net/s/1/1/x", robots, 1.0)

    assert decision.allowed is True
    assert decision.reason
    assert str(decision.robots_url) == "https://www.fanfiction.net/robots.txt"
    assert decision.robots_sha256 == hashlib.sha256(robots.encode("utf-8")).hexdigest()
    assert decision.effective_delay_seconds == 5.0


def test_policy_keeps_requested_delay_when_it_is_largest() -> None:
    robots = "User-agent: *\nAllow: /\nCrawl-delay: 6\n"
    decision = evaluate_policy("https://www.fanfiction.net/s/1/1/x", robots, 7.5)
    assert decision.effective_delay_seconds == 7.5
