"""Minimal source configuration for v1 prototype collection."""

from __future__ import annotations

from typing import List, Dict


def load_sources() -> List[Dict[str, str]]:
    """Return a minimal list of free sources for crypto, US, and forex/macro news."""
    return [
        {
            "name": "CoinDesk RSS",
            "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "market": "crypto",
        },
        {
            "name": "Cointelegraph Bitcoin RSS",
            "url": "https://cointelegraph.com/rss/tag/bitcoin",
            "market": "crypto",
        },
        {
            "name": "CNBC Top News RSS",
            "url": "https://www.cnbc.com/?format=rss",
            "market": "us",
        },
        {
            "name": "CNBC Markets RSS",
            "url": "https://www.cnbc.com/markets/?format=rss",
            "market": "us",
        },
        {
            "name": "FXStreet News RSS",
            "url": "https://www.fxstreet.com/rss/news",
            "market": "forex_macro",
        },
        {
            "name": "Federal Reserve All Press Releases RSS",
            "url": "https://www.federalreserve.gov/feeds/press_all.xml",
            "market": "forex_macro",
        },
    ]
