"""Normalize raw feed items into the minimal v1 news_item format."""

from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
import json
import urllib.parse
import urllib.request
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

TRANSLATION_TIMEOUT_SECONDS = 5
_TRANSLATION_CACHE: Dict[str, str] = {}


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

            raw_description = (raw.get("description") or "").strip()
            raw_summary = (raw.get("summary") or "").strip()
            text_for_assets = raw_description or raw_summary
            related_assets = _extract_related_assets(title, text_for_assets, result.market)
            if related_assets:
                item["related_assets"] = related_assets

            if raw_description:
                item["description"] = raw_description
            if raw_summary:
                item["summary"] = raw_summary

            description_for_translation = raw_description or raw_summary
            if description_for_translation:
                item["zh_description"] = translate_to_zh_hant(description_for_translation)

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


def translate_to_zh_hant(text: str) -> str:
    content = (text or "").strip()
    if not content:
        return ""

    cached = _TRANSLATION_CACHE.get(content)
    if cached is not None:
        return cached

    translated = _translate_via_google_free(content)
    if not _looks_translated_to_zh_hant(translated, content):
        translated = _translate_via_mymemory_free(content)
    if not _looks_translated_to_zh_hant(translated, content):
        translated = content

    _TRANSLATION_CACHE[content] = translated
    return translated


def _translate_via_google_free(text: str) -> str:
    params = urllib.parse.urlencode(
        {
            "client": "gtx",
            "sl": "en",
            "tl": "zh-TW",
            "dt": "t",
            "q": text,
        }
    )
    url = f"https://translate.googleapis.com/translate_a/single?{params}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "market-briefing-prototype/0.1"},
    )

    try:
        with urllib.request.urlopen(request, timeout=TRANSLATION_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 - keep pipeline resilient on translation failures
        return ""

    if not isinstance(payload, list) or not payload:
        return ""
    parts = payload[0]
    if not isinstance(parts, list):
        return ""

    translated_chunks: List[str] = []
    for row in parts:
        if not isinstance(row, list) or not row:
            continue
        piece = row[0]
        if isinstance(piece, str) and piece.strip():
            translated_chunks.append(piece)

    return unescape("".join(translated_chunks)).strip()


def _translate_via_mymemory_free(text: str) -> str:
    params = urllib.parse.urlencode(
        {
            "q": text,
            "langpair": "en|zh-TW",
        }
    )
    url = f"https://api.mymemory.translated.net/get?{params}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "market-briefing-prototype/0.1"},
    )

    try:
        with urllib.request.urlopen(request, timeout=TRANSLATION_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 - keep pipeline resilient on translation failures
        return ""

    translated = payload.get("responseData", {}).get("translatedText")
    if isinstance(translated, str):
        return unescape(translated).strip()
    return ""


def _looks_translated_to_zh_hant(candidate: str, source: str) -> bool:
    if not candidate or not candidate.strip():
        return False
    normalized_candidate = candidate.strip()
    normalized_source = source.strip()
    if normalized_candidate.lower() == normalized_source.lower():
        return False
    return _contains_cjk(normalized_candidate)


def _contains_cjk(text: str) -> bool:
    for ch in text:
        codepoint = ord(ch)
        if 0x4E00 <= codepoint <= 0x9FFF:
            return True
    return False
