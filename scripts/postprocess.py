"""Minimal filtering, deduplication, and rule-based ranking for v1."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
import re
from typing import Dict, List, Set


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}

MACRO_KEYWORDS = {
    "fomc",
    "cpi",
    "ppi",
    "nfp",
    "ism",
    "federal reserve",
    "fed",
    "central bank",
    "interest rate",
    "inflation",
}

CORE_ASSETS = {
    "NVDA",
    "AAPL",
    "MSFT",
    "AMZN",
    "META",
    "TSLA",
    "PLTR",
    "COHR",
    "QQQ",
    "SMH",
    "SHLD",
    "BTC",
    "ETH",
}

ASSET_KEYWORDS = {
    "NVDA": ["nvda", "nvidia"],
    "AAPL": ["aapl", "apple"],
    "MSFT": ["msft", "microsoft"],
    "AMZN": ["amzn", "amazon"],
    "META": ["meta"],
    "TSLA": ["tsla", "tesla"],
    "PLTR": ["pltr", "palantir"],
    "COHR": ["cohr", "coherent"],
    "QQQ": ["qqq"],
    "SMH": ["smh"],
    "SHLD": ["shld"],
    "BTC": ["btc", "bitcoin"],
    "ETH": ["eth", "ethereum"],
}


def process_items(
    items: List[Dict[str, object]],
    report_markets: Set[str],
    recent_hours: int,
    top_n: int = 10,
) -> List[Dict[str, object]]:
    filtered = filter_items(items, report_markets, recent_hours)
    deduped = deduplicate_items(filtered)
    ranked = rank_items(deduped)
    return ranked[:top_n]


def filter_items(items: List[Dict[str, object]], report_markets: Set[str], recent_hours: int) -> List[Dict[str, object]]:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=recent_hours)

    filtered: List[Dict[str, object]] = []
    for item in items:
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        published_at = str(item.get("published_at", "")).strip()
        market = str(item.get("market", "")).strip().lower()

        if not title or not url or not published_at:
            continue
        if market not in report_markets:
            continue

        dt = _parse_datetime(published_at)
        if dt is None:
            continue
        if dt < cutoff:
            continue

        filtered.append(item)

    return filtered


def deduplicate_items(items: List[Dict[str, object]]) -> List[Dict[str, object]]:
    kept: List[Dict[str, object]] = []
    for item in items:
        duplicate_index = _find_duplicate_index(kept, item)
        if duplicate_index == -1:
            kept.append(item)
            continue

        existing = kept[duplicate_index]
        if _get_datetime(item) >= _get_datetime(existing):
            kept[duplicate_index] = item

    return kept


def rank_items(items: List[Dict[str, object]]) -> List[Dict[str, object]]:
    def rank_key(item: Dict[str, object]) -> tuple[int, int, float]:
        text = _item_text(item)
        has_macro = int(any(keyword in text for keyword in MACRO_KEYWORDS))
        has_core_asset = int(_contains_core_asset(item))
        recency = _get_datetime(item).timestamp()
        return (has_macro, has_core_asset, recency)

    return sorted(items, key=rank_key, reverse=True)


def _find_duplicate_index(kept: List[Dict[str, object]], candidate: Dict[str, object]) -> int:
    cand_title = str(candidate.get("title", ""))
    cand_tokens = _tokens(cand_title)

    for idx, existing in enumerate(kept):
        existing_title = str(existing.get("title", ""))
        title_similarity = SequenceMatcher(None, cand_title.lower(), existing_title.lower()).ratio()
        if title_similarity >= 0.86:
            return idx

        existing_tokens = _tokens(existing_title)
        overlap = _keyword_overlap(cand_tokens, existing_tokens)
        if overlap >= 0.7:
            return idx

    return -1


def _keyword_overlap(left: Set[str], right: Set[str]) -> float:
    if not left or not right:
        return 0.0
    shared = left.intersection(right)
    base = min(len(left), len(right))
    if base == 0:
        return 0.0
    return len(shared) / base


def _tokens(text: str) -> Set[str]:
    parts = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {p for p in parts if p not in STOPWORDS and len(p) > 1}


def _contains_core_asset(item: Dict[str, object]) -> bool:
    related = item.get("related_assets")
    if isinstance(related, list):
        for symbol in related:
            if str(symbol).upper() in CORE_ASSETS:
                return True

    text = _item_text(item)
    for _, keywords in ASSET_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return True
    return False


def _item_text(item: Dict[str, object]) -> str:
    title = str(item.get("title", "")).lower()
    summary = str(item.get("summary", "")).lower()
    return f"{title} {summary}".strip()


def _get_datetime(item: Dict[str, object]) -> datetime:
    published_at = str(item.get("published_at", "")).strip()
    parsed = _parse_datetime(published_at)
    if parsed is None:
        return datetime.min.replace(tzinfo=timezone.utc)
    return parsed


def _parse_datetime(text: str) -> datetime | None:
    value = text.strip()
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
