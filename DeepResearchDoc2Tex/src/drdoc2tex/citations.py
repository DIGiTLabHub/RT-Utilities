from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qsl, urlparse, urlunparse, urlencode


@dataclass(frozen=True)
class Citation:
    number: int
    url: str


def normalize_url(url: str) -> str:
    parts = urlparse(url)
    query = [(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_")]
    return urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, urlencode(query), ""))


def key_for_number(number: int) -> str:
    return f"key-{number}"
