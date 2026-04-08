"""Minimal collector for RSS/Atom sources using Python standard library."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple


@dataclass
class SourceResult:
    source_name: str
    source_url: str
    market: str
    raw_items: List[Dict[str, str]]


def collect_sources(sources: List[Dict[str, str]], timeout_seconds: int = 15) -> Tuple[List[SourceResult], List[Dict[str, str]]]:
    """Fetch sources and parse raw feed entries; continue on failures."""
    results: List[SourceResult] = []
    errors: List[Dict[str, str]] = []

    for src in sources:
        try:
            text = _fetch_text(src["url"], timeout_seconds)
            raw_items = _parse_feed_items(text)
            results.append(
                SourceResult(
                    source_name=src["name"],
                    source_url=src["url"],
                    market=src["market"],
                    raw_items=raw_items,
                )
            )
        except Exception as exc:  # noqa: BLE001 - simple prototype failure capture
            errors.append(
                {
                    "source": src["name"],
                    "url": src["url"],
                    "error": str(exc),
                    "logged_at": datetime.now(timezone.utc).isoformat(),
                }
            )

    return results, errors


def _fetch_text(url: str, timeout_seconds: int) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "market-briefing-prototype/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"fetch failed: {exc}") from exc


def _parse_feed_items(xml_text: str) -> List[Dict[str, str]]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise RuntimeError(f"invalid feed XML: {exc}") from exc

    local_name = _local_tag(root.tag)
    if local_name == "rss":
        return _parse_rss(root)
    if local_name == "feed":
        return _parse_atom(root)
    raise RuntimeError(f"unsupported feed root tag: {local_name}")


def _parse_rss(root: ET.Element) -> List[Dict[str, str]]:
    channel = root.find("channel")
    if channel is None:
        return []

    items: List[Dict[str, str]] = []
    for item in channel.findall("item"):
        items.append(
            {
                "title": _text(item.find("title")),
                "url": _text(item.find("link")),
                "published_at": _text(item.find("pubDate")),
                "summary": _text(item.find("description")),
            }
        )
    return items


def _parse_atom(root: ET.Element) -> List[Dict[str, str]]:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items: List[Dict[str, str]] = []
    for entry in root.findall("a:entry", ns):
        link = ""
        link_el = entry.find("a:link", ns)
        if link_el is not None:
            link = link_el.attrib.get("href", "")

        published = _text(entry.find("a:published", ns)) or _text(entry.find("a:updated", ns))
        summary = _text(entry.find("a:summary", ns)) or _text(entry.find("a:content", ns))

        items.append(
            {
                "title": _text(entry.find("a:title", ns)),
                "url": link,
                "published_at": published,
                "summary": summary,
            }
        )
    return items


def _local_tag(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _text(element: ET.Element | None) -> str:
    if element is None or element.text is None:
        return ""
    return element.text.strip()
