from __future__ import annotations

import hashlib
from urllib.parse import urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

from pydantic import Field, HttpUrl

from .models import StrictModel


class PolicyDecision(StrictModel):
    allowed: bool
    reason: str = Field(min_length=1)
    robots_url: HttpUrl
    robots_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    effective_delay_seconds: float = Field(ge=0)


def evaluate_policy(
    url: str, robots_text: str, requested_delay: float
) -> PolicyDecision:
    parsed_url = urlsplit(url)
    robots_url = urlunsplit(
        (parsed_url.scheme, parsed_url.netloc, "/robots.txt", "", "")
    )
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_text.splitlines())

    allowed = parser.can_fetch("*", url)
    robots_delay = parser.crawl_delay("*")
    numeric_robots_delay = (
        float(robots_delay)
        if isinstance(robots_delay, (int, float)) and not isinstance(robots_delay, bool)
        else 0.0
    )

    return PolicyDecision(
        allowed=allowed,
        reason=(
            "allowed by robots.txt"
            if allowed
            else "disallowed by robots.txt for user-agent *"
        ),
        robots_url=robots_url,
        robots_sha256=hashlib.sha256(robots_text.encode("utf-8")).hexdigest(),
        effective_delay_seconds=max(
            5.0, float(requested_delay), numeric_robots_delay
        ),
    )
