"""Normalize raw feed items into the minimal v1 news_item format."""

from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Dict, List

from collector import SourceResult


CRYPTO_ASSET_KEYWORDS = {
    "BTC": ["btc", "bitcoin"],
    "ETH": ["eth", "ethereum"],
}

US_ASSET_KEYWORDS = {
    "NVDA": ["nvda", "nvidia"],
    "AAPL": ["aapl", "apple"],
    "MSFT": ["msft", "microsoft"],
    "AMZN": ["amzn", "amazon"],
    "META": ["meta"],
    "TSLA": ["tsla", "tesla"],
    "PLTR": ["pltr", "palantir"],
    "QQQ": ["qqq"],
    "SMH": ["smh"],
}

FOREX_MACRO_KEYWORDS = {
    "XAUUSD": ["xauusd", "gold", "bullion"],
    "EURUSD": ["eurusd", "eur/usd"],
    "GBPUSD": ["gbpusd", "gbp/usd"],
    "USDJPY": ["usdjpy", "usd/jpy"],
    "DXY": ["dxy", "dollar index", "us dollar index"],
    "FOMC": ["fomc", "federal open market committee"],
    "CPI": ["cpi", "consumer price index", "inflation"],
    "PPI": ["ppi", "producer price index"],
    "NFP": ["nfp", "nonfarm payroll", "non-farm payroll"],
    "ISM": ["ism"],
    "Fed": ["federal reserve", "fed"],
    "ECB": ["ecb", "european central bank"],
    "BOJ": ["boj", "bank of japan"],
    "BOE": ["boe", "bank of england"],
    "Central Banks": ["central bank", "central banks"],
}


def normalize_items(results: List[SourceResult]) -> List[Dict[str, object]]:
    normalized: List[Dict[str, object]] = []
    for result in results:
        for raw in result.raw_items:
            title = (raw.get("title") or "").strip()
            url = (raw.get("url") or "").strip()

            if not title or not url:
                continue

            item: Dict[str, object] = {
                "title": title,
                "source": result.source_name,
                "url": url,
                "published_at": _normalize_published_at(raw.get("published_at", "")),
                "market": result.market,
            }

            related_assets = _extract_related_assets(title, raw.get("summary", ""), result.market)
            if related_assets:
                item["related_assets"] = related_assets

            summary = (raw.get("summary") or "").strip()
            if summary:
                item["summary"] = summary

            normalized.append(item)

    return normalized


def _normalize_published_at(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""

    try:
        return parsedate_to_datetime(text).isoformat()
    except (TypeError, ValueError):
        pass

    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return text


def _extract_related_assets(title: str, summary: str, market: str) -> List[str]:
    haystack = f"{title} {summary}".lower()
    found: List[str] = []

    if market == "crypto":
        mapping = CRYPTO_ASSET_KEYWORDS
    elif market == "us":
        mapping = US_ASSET_KEYWORDS
    elif market == "forex_macro":
        mapping = FOREX_MACRO_KEYWORDS
    else:
        mapping = {}

    for asset, keywords in mapping.items():
        if any(keyword in haystack for keyword in keywords):
            found.append(asset)

    return found
