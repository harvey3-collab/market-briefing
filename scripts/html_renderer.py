"""Minimal HTML report renderer for processed market briefing items."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re
from typing import Dict, List

MARKET_ORDER = ["us", "forex_macro", "crypto"]
MARKET_LABELS = {
    "us": "美股",
    "forex_macro": "外匯與總經",
    "crypto": "加密貨幣",
}
EMPTY_MESSAGE_ALL_SOURCES_FAILED = "目前尚無可用資料"
EMPTY_MESSAGE_NO_MAJOR_EVENTS = "目前無重大市場事件"
FUTURE_BRIEF_FIELDS = ("zh_summary", "brief", "takeaway", "highlight")
LEGACY_BRIEF_FIELDS = ("zh_description", "summary", "description")
REPORT_BRIEF_FIELDS = (
    "report_zh_summary",
    "report_brief",
    "report_takeaway",
    "report_highlight",
    "report_summary",
    "market_summary",
    "daily_summary",
)


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
    display_date = escape(_format_display_date(generated_at))
    summary_text = _extract_report_summary(items)
    summary_html = escape(summary_text) if summary_text else " "
    summary_state_class = "" if summary_text else " is-empty"
    jump_nav_html = _build_jump_nav(items)
    takeaways_html = _build_takeaways_block(items)
    sections_html = _build_sections(items)
    count = len(items)

    if count == 0:
        empty_message = EMPTY_MESSAGE_ALL_SOURCES_FAILED if all_sources_failed else EMPTY_MESSAGE_NO_MAJOR_EVENTS
        sections_html = f'<article class="empty">{escape(empty_message)}</article>'

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>每日市場晨報</title>
  <style>
    :root {{
      --bg: #f3f6fb;
      --bg-soft: #f8fbff;
      --surface: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --border: #dce5f1;
      --accent: #1d4ed8;
      --accent-soft: #dbeafe;
      --radius-lg: 14px;
      --radius-md: 11px;
      --radius-pill: 999px;
      --shadow-sm: 0 2px 6px rgba(15, 23, 42, 0.045);
      --shadow-md: 0 8px 22px rgba(15, 23, 42, 0.07);
    }}
    body {{
      margin: 0;
      line-height: 1.6;
      color: var(--text);
      background: linear-gradient(180deg, #edf3fb 0%, var(--bg) 240px);
      font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    }}
    .container {{
      max-width: 920px;
      margin: 0 auto;
      padding: 24px 18px 34px;
    }}
    .panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-sm);
    }}
    .panel-title {{
      margin: 0 0 8px;
      font-size: 19px;
      line-height: 1.3;
      font-weight: 700;
      letter-spacing: 0.1px;
    }}
    .hero {{
      position: relative;
      padding: 24px 24px 20px;
      margin-bottom: 12px;
      overflow: hidden;
    }}
    .hero::before {{
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: 3px;
      background: linear-gradient(90deg, var(--accent) 0%, #60a5fa 72%, #bfdbfe 100%);
    }}
    .hero h1 {{
      margin: 0;
      font-size: 31px;
      line-height: 1.2;
      letter-spacing: 0.1px;
    }}
    .hero-subtitle {{
      margin: 9px 0 0;
      font-size: 15px;
      color: var(--muted);
    }}
    .hero-meta {{
      margin-top: 13px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      font-size: 13px;
      color: #334155;
    }}
    .meta-pill {{
      border: 1px solid var(--border);
      border-radius: var(--radius-pill);
      padding: 5px 10px;
      background: #f8fafc;
    }}
    .jump-nav {{
      position: sticky;
      top: 10px;
      z-index: 10;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 8px 10px;
      margin: 0 0 12px;
      background: rgba(250, 252, 255, 0.92);
      backdrop-filter: blur(4px);
    }}
    .jump-link {{
      display: inline-block;
      font-size: 12px;
      text-decoration: none;
      color: #1e3a8a;
      background: #eff6ff;
      border: 1px solid var(--accent-soft);
      border-radius: var(--radius-pill);
      padding: 3px 9px;
      font-weight: 600;
    }}
    .jump-link:hover {{
      background: #dbeafe;
    }}
    .summary {{
      padding: 14px 16px;
      margin-bottom: 14px;
    }}
    .takeaways {{
      background: linear-gradient(180deg, var(--bg-soft) 0%, #ffffff 100%);
      border-color: #c9dcfb;
      box-shadow: var(--shadow-md);
      padding: 14px 16px;
      margin-bottom: 14px;
    }}
    .takeaways h2 {{
      margin: 0 0 9px;
    }}
    .takeaway-list {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .takeaway-item {{
      border: 1px solid #d7e6ff;
      background: #ffffff;
      border-radius: var(--radius-md);
      padding: 7px 9px;
      color: #1e293b;
      font-size: 13px;
      line-height: 1.55;
    }}
    .takeaway-label {{
      color: var(--accent);
      font-weight: 700;
      margin-right: 6px;
    }}
    .summary h2 {{
      margin: 0 0 8px;
    }}
    .summary-content {{
      margin: 0;
      color: #334155;
      white-space: pre-wrap;
      min-height: 22px;
      font-size: 13px;
      line-height: 1.6;
    }}
    .summary-content.is-empty {{
      color: #7b8798;
      font-style: italic;
      border: 1px dashed #d8e1ee;
      border-radius: var(--radius-md);
      padding: 8px 10px;
      background: #f8fafd;
    }}
    .cards {{
      display: flex;
      flex-direction: column;
      gap: 9px;
    }}
    .section {{
      margin-bottom: 18px;
      padding: 8px 0 2px;
      border-top: 1px dashed #d8e2f0;
    }}
    .section-head {{
      margin: 0 0 8px;
      padding: 3px 3px 5px;
      border-left: 3px solid var(--accent-soft);
      padding-left: 10px;
    }}
    .section h2 {{
      margin: 0 0 8px;
      font-size: 21px;
      line-height: 1.25;
      padding-bottom: 4px;
    }}
    .section-intro {{
      margin: 0;
      color: #475569;
      font-size: 13px;
      line-height: 1.6;
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 12px 14px;
      box-shadow: var(--shadow-sm);
      transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }}
    .card:hover {{
      transform: translateY(-1px);
      box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08);
    }}
    .cards .card:nth-child(-n+2) {{
      border-color: #cadbfd;
      box-shadow: 0 3px 10px rgba(37, 99, 235, 0.08);
    }}
    .cards .card:nth-child(n+3) {{
      background: #fbfdff;
    }}
    .card h3 {{
      margin: 0;
      font-size: 17px;
      line-height: 1.35;
      font-weight: 700;
    }}
    .card h3 a {{
      color: var(--text);
      text-decoration: none;
    }}
    .card h3 a:hover {{
      text-decoration: underline;
    }}
    .highlight-line {{
      margin: 7px 0 8px;
      padding: 5px 8px;
      border-left: 3px solid #93c5fd;
      background: #f8fbff;
      color: #0f172a;
      font-size: 13px;
      line-height: 1.5;
      border-radius: 0 8px 8px 0;
    }}
    .highlight-label {{
      color: var(--accent);
      font-weight: 700;
      margin-right: 6px;
    }}
    .description {{
      margin: 0 0 8px;
      font-size: 13px;
      color: #334155;
      line-height: 1.55;
    }}
    .tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin: 0 0 7px;
    }}
    .tag {{
      border: 1px solid #bfdbfe;
      background: #eff6ff;
      color: var(--accent);
      font-size: 11px;
      font-weight: 600;
      border-radius: var(--radius-pill);
      padding: 1px 7px;
    }}
    .meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 12px;
      color: var(--muted);
    }}
    .meta-item {{
      white-space: nowrap;
    }}
    .meta-item strong {{
      color: #475569;
      font-weight: 600;
      margin-right: 3px;
    }}
    .empty {{
      padding: 13px 14px;
      background: #f8fafd;
      border: 1px dashed #cfd8e6;
      border-radius: var(--radius-md);
      color: #475569;
      font-size: 13px;
    }}
    .page-footer {{
      margin-top: 18px;
      padding-top: 10px;
      border-top: 1px solid var(--border);
      font-size: 12px;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main class="container">
    <header class="hero panel">
      <h1>每日市場晨報</h1>
      <p class="hero-subtitle">掌握今日關鍵市場動態</p>
      <div class="hero-meta">
        <span class="meta-pill">報告日期: {display_date}</span>
        <span class="meta-pill">更新時間: {safe_generated_at}</span>
        <span class="meta-pill">重點條目: {count}</span>
      </div>
    </header>

    {jump_nav_html}

    {takeaways_html}

    <section class="summary panel">
      <h2 class="panel-title">重點摘要</h2>
      <p class="summary-content{summary_state_class}">{summary_html}</p>
    </section>

    <section>
      {sections_html}
    </section>

    <footer class="page-footer">
      報告產生時間: {safe_generated_at}
    </footer>
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
        intro = escape(_build_section_intro(market_items))
        cards_html = _build_cards(market_items)
        sections.append(
            f"""<section class="section" id="section-{escape(market)}">
  <div class="section-head">
    <h2>{title}</h2>
    <p class="section-intro">{intro}</p>
  </div>
  <div class="cards">
    {cards_html}
  </div>
</section>"""
        )

    return "\n".join(sections)


def _build_jump_nav(items: List[Dict[str, object]]) -> str:
    links: List[str] = []
    for market in MARKET_ORDER:
        has_items = any(str(item.get("market", "")).lower() == market for item in items)
        if not has_items:
            continue
        label = escape(MARKET_LABELS.get(market, market))
        links.append(f'<a class="jump-link" href="#section-{escape(market)}">{label}</a>')

    if not links:
        return ""

    joined = "\n      ".join(links)
    return f"""<nav class="jump-nav panel" aria-label="分區快速導覽">
      {joined}
    </nav>"""


def _build_takeaways_block(items: List[Dict[str, object]]) -> str:
    takeaways = _derive_takeaways(items)
    rows = "".join(
        f'<li class="takeaway-item"><span class="takeaway-label">重點</span>{escape(line)}</li>'
        for line in takeaways
    )
    return f"""<section class="takeaways panel">
      <h2 class="panel-title">今日重點</h2>
      <ul class="takeaway-list">
        {rows}
      </ul>
    </section>"""


def _build_cards(items: List[Dict[str, object]]) -> str:
    parts: List[str] = []
    for item in items:
        title_text = str(item.get("title", "")).strip()
        title = escape(title_text)
        url = escape(str(item.get("url", "")))
        source = escape(str(item.get("source", "")))
        published_at = escape(_format_published_at(str(item.get("published_at", ""))))
        brief_text = _select_item_brief_text(item)
        description_source = _select_item_supporting_text(item, preferred=brief_text)
        description = _prepare_description(description_source, max_chars=132) or "暫無補充說明。"
        highlight = _derive_highlight_line(brief_text=brief_text, description=description_source, title=title_text)
        related_assets = item.get("related_assets")

        tags_html = ""
        asset_tags = _extract_asset_tags(related_assets)
        if asset_tags:
            tags = "".join(f'<span class="tag">{escape(tag)}</span>' for tag in asset_tags)
            tags_html = f'<div class="tags">{tags}</div>'

        parts.append(
            f"""<article class="card">
  <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
  <p class="highlight-line"><span class="highlight-label">重點一句話</span>{escape(highlight)}</p>
  <p class="description">{escape(description)}</p>
  {tags_html}
  <div class="meta-row">
    <span class="meta-item"><strong>來源:</strong>{source}</span>
    <span class="meta-item"><strong>發布時間:</strong>{published_at}</span>
  </div>
</article>"""
        )

    return "\n".join(parts)


def _extract_report_summary(items: List[Dict[str, object]]) -> str:
    for item in items:
        report_value = _select_first_text(item, REPORT_BRIEF_FIELDS)
        if report_value:
            return report_value
    return ""


def _derive_takeaways(items: List[Dict[str, object]]) -> List[str]:
    if not items:
        return ["目前資料有限，稍後更新本日市場重點。"]

    takeaways: List[str] = []
    market_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    asset_counts: Counter[str] = Counter()
    latest_dt: datetime | None = None

    for item in items:
        market = str(item.get("market", "")).strip().lower()
        if market:
            market_counts[market] += 1

        source = str(item.get("source", "")).strip()
        if source:
            source_counts[source] += 1

        parsed = _parse_datetime(str(item.get("published_at", "")).strip())
        if parsed is not None and (latest_dt is None or parsed > latest_dt):
            latest_dt = parsed

        for tag in _extract_asset_tags(item.get("related_assets")):
            asset_counts[tag] += 1

    if market_counts:
        market, count = market_counts.most_common(1)[0]
        label = MARKET_LABELS.get(market, market)
        takeaways.append(f"{label}相關訊息數量最多（{count} 則），建議優先關注。")

    if asset_counts:
        top_assets = [name for name, _ in asset_counts.most_common(3)]
        takeaways.append(f"高頻關注標的集中在 {', '.join(top_assets)}。")

    if source_counts:
        source, count = source_counts.most_common(1)[0]
        takeaways.append(f"主要資訊來源為 {source}（{count} 則）。")

    if latest_dt is not None:
        takeaways.append(f"最新發布時間約為 {latest_dt.strftime('%Y-%m-%d %H:%M UTC')}。")

    covered_markets = [MARKET_LABELS.get(m, m) for m, c in market_counts.items() if c > 0]
    if covered_markets:
        sample = "、".join(covered_markets[:3])
        takeaways.append(f"本次涵蓋 {len(covered_markets)} 個市場類別：{sample}。")

    if not takeaways:
        return ["本頁整理今日主要市場動態，請搭配各分區卡片查看細節。"]

    return takeaways[:5]


def _build_section_intro(items: List[Dict[str, object]]) -> str:
    if not items:
        return "本區整理今日相關市場動態。"

    count = len(items)
    source_counter: Counter[str] = Counter()
    latest_dt: datetime | None = None
    assets: set[str] = set()

    for item in items:
        source = str(item.get("source", "")).strip()
        if source:
            source_counter[source] += 1

        parsed = _parse_datetime(str(item.get("published_at", "")).strip())
        if parsed is not None and (latest_dt is None or parsed > latest_dt):
            latest_dt = parsed

        related_assets = item.get("related_assets")
        if isinstance(related_assets, list):
            for asset in related_assets:
                text = str(asset).strip().upper()
                if text:
                    assets.add(text)

    if not source_counter and latest_dt is None and not assets:
        section_brief = _select_first_section_brief(items)
        if section_brief:
            return f"本區重點：{_prepare_description(section_brief, max_chars=72)}"
        return "本區整理今日相關市場動態。"

    lead = f"本區收錄 {count} 則市場動態"
    if source_counter:
        top_source, _ = source_counter.most_common(1)[0]
        lead += f"，資訊來源以 {top_source} 為主"
    lead += "。"

    details: List[str] = []
    if latest_dt is not None:
        details.append(f"最新發布時間約為 {latest_dt.strftime('%Y-%m-%d %H:%M UTC')}")
    if assets:
        top_assets = sorted(assets)[:3]
        details.append(f"重點標的包含 {', '.join(top_assets)}")

    if details:
        return f"{lead} {'；'.join(details)}。"
    return lead


def _extract_asset_tags(value: object) -> List[str]:
    if not isinstance(value, list):
        return []

    tags: List[str] = []
    seen: set[str] = set()
    for raw in value:
        text = str(raw).strip().upper()
        if not text or text in seen:
            continue
        seen.add(text)
        tags.append(text)
        if len(tags) >= 6:
            break
    return tags


def _derive_highlight_line(*, brief_text: str, description: str, title: str) -> str:
    if brief_text.strip():
        line = _prepare_description(brief_text, max_chars=92)
        if line:
            return line

    if description.strip():
        line = _prepare_description(description, max_chars=92)
        if line:
            return line

    title_line = _prepare_description(title, max_chars=80)
    if title_line:
        return f"焦點在於「{title_line}」。"
    return "本則重點資訊待補充。"


def _select_first_text(item: Dict[str, object], fields: tuple[str, ...]) -> str:
    for field in fields:
        value = item.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _select_item_brief_text(item: Dict[str, object]) -> str:
    return _select_first_text(item, FUTURE_BRIEF_FIELDS + LEGACY_BRIEF_FIELDS)


def _select_item_supporting_text(item: Dict[str, object], *, preferred: str) -> str:
    primary = _prepare_description(preferred, max_chars=220)
    for field in FUTURE_BRIEF_FIELDS + LEGACY_BRIEF_FIELDS:
        value = item.get(field)
        if not isinstance(value, str) or not value.strip():
            continue
        cleaned = _prepare_description(value, max_chars=220)
        if not cleaned:
            continue
        if primary and cleaned == primary:
            continue
        return value.strip()
    return preferred


def _select_first_section_brief(items: List[Dict[str, object]]) -> str:
    for item in items:
        text = _select_item_brief_text(item)
        if text:
            return text
    return ""


def _prepare_description(text: str, *, max_chars: int) -> str:
    cleaned = _strip_html(text)
    normalized = _normalize_whitespace(cleaned)
    if not normalized:
        return ""
    return _truncate_text(normalized, max_chars=max_chars)


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _truncate_text(text: str, *, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text

    cut = text[: max_chars + 1]
    last_space = cut.rfind(" ")
    if last_space >= max_chars // 2:
        cut = cut[:last_space]
    else:
        cut = cut[:max_chars]
    return cut.rstrip(" ,.;:") + "…"


def _parse_datetime(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_display_date(value: str) -> str:
    text = value.strip()
    if not text:
        return "N/A"

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return text


def _format_published_at(value: str) -> str:
    parsed = _parse_datetime(value)
    if parsed is None:
        return value.strip()
    return parsed.strftime("%Y-%m-%d %H:%M UTC")
