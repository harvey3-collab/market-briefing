"""Minimal HTML report renderer for processed market briefing items."""

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Dict, List

MARKET_ORDER = ["us", "forex_macro", "crypto"]
MARKET_LABELS = {
    "us": "美股",
    "forex_macro": "外匯與總經",
    "crypto": "加密貨幣",
}


def render_report_html(
    *,
    items: List[Dict[str, object]],
    generated_at: str,
    output_path: Path,
    all_sources_failed: bool,
) -> None:
    """Render a simple readable HTML report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    content = _build_page(items=items, generated_at=generated_at, all_sources_failed=all_sources_failed)
    output_path.write_text(content, encoding="utf-8")


def _build_page(*, items: List[Dict[str, object]], generated_at: str, all_sources_failed: bool) -> str:
    safe_generated_at = escape(generated_at)
    sections_html = _build_sections(items)
    count = len(items)

    if count == 0:
        empty_message = "目前無可用資料" if all_sources_failed else "目前無重大事件"
        sections_html = f'<p class="empty">{escape(empty_message)}</p>'

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>市場晨報</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
      margin: 24px;
      line-height: 1.5;
      color: #1f2937;
      background: #f8fafc;
    }}
    .container {{
      max-width: 860px;
      margin: 0 auto;
    }}
    h1 {{
      margin-bottom: 8px;
    }}
    .meta {{
      color: #4b5563;
      margin-bottom: 20px;
    }}
    .cards {{
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .section {{
      margin-bottom: 20px;
    }}
    .section h2 {{
      margin: 0 0 10px 0;
      font-size: 20px;
      color: #0f172a;
    }}
    .card {{
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 12px 14px;
    }}
    .card h3 {{
      font-size: 18px;
      margin: 0 0 8px 0;
    }}
    .card h3 a {{
      color: #0f172a;
      text-decoration: none;
    }}
    .card h3 a:hover {{
      text-decoration: underline;
    }}
    .row {{
      font-size: 14px;
      color: #374151;
      margin: 2px 0;
    }}
    .label {{
      font-weight: 600;
      margin-right: 6px;
    }}
    .empty {{
      padding: 16px;
      background: #ffffff;
      border: 1px dashed #cbd5e1;
      border-radius: 10px;
    }}
  </style>
</head>
<body>
  <main class="container">
    <h1>市場晨報</h1>
    <div class="meta">
      <div>更新時間: {safe_generated_at}</div>
      <div>條目數: {count}</div>
    </div>
    <section>
      {sections_html}
    </section>
  </main>
</body>
</html>
"""


def _build_sections(items: List[Dict[str, object]]) -> str:
    sections: List[str] = []
    for market in MARKET_ORDER:
        market_items = [item for item in items if str(item.get("market", "")).lower() == market]
        if not market_items:
            continue

        title = escape(MARKET_LABELS.get(market, market))
        cards_html = _build_cards(market_items)
        sections.append(
            f"""<section class="section">
  <h2>{title}</h2>
  <div class="cards">
    {cards_html}
  </div>
</section>"""
        )

    return "\n".join(sections)


def _build_cards(items: List[Dict[str, object]]) -> str:
    parts: List[str] = []
    for item in items:
        title = escape(str(item.get("title", "")))
        url = escape(str(item.get("url", "")))
        source = escape(str(item.get("source", "")))
        published_at = escape(_format_published_at(str(item.get("published_at", ""))))
        summary = str(item.get("summary", "")).strip()
        related_assets = item.get("related_assets")

        summary_html = ""
        if summary:
            summary_html = f'<div class="row"><span class="label">摘要:</span>{escape(summary)}</div>'

        assets_html = ""
        if isinstance(related_assets, list) and related_assets:
            joined = ", ".join(str(asset) for asset in related_assets)
            assets_html = f'<div class="row"><span class="label">相關標的:</span>{escape(joined)}</div>'

        parts.append(
            f"""<article class="card">
  <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
  <div class="row"><span class="label">來源:</span>{source}</div>
  <div class="row"><span class="label">發布時間:</span>{published_at}</div>
  {summary_html}
  {assets_html}
</article>"""
        )

    return "\n".join(parts)


def _format_published_at(value: str) -> str:
    text = value.strip()
    if not text:
        return text

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)
        return parsed.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return text
