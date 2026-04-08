"""Run minimal v1 collection + normalization and write JSON output."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict

from collector import collect_sources
from html_renderer import render_report_html
from normalizer import normalize_items
from postprocess import process_items
from source_config import load_sources


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_FILE = OUTPUT_DIR / "report_items.json"
HTML_OUTPUT_FILE = OUTPUT_DIR / "report.html"
ERROR_LOG_FILE = OUTPUT_DIR / "collection_errors.log"
REPORT_MARKETS = {"crypto", "us", "forex_macro"}
RECENT_HOURS = 72
TOP_N = 10


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sources = load_sources()
    collected, errors = collect_sources(sources)
    normalized_items = normalize_items(collected)
    items = process_items(
        normalized_items,
        report_markets=REPORT_MARKETS,
        recent_hours=RECENT_HOURS,
        top_n=TOP_N,
    )
    generated_at = datetime.now(timezone.utc).isoformat()

    payload: Dict[str, object] = {
        "generated_at": generated_at,
        "item_count": len(items),
        "items": items,
    }
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    all_sources_failed = len(collected) == 0 and len(errors) > 0
    render_report_html(
        items=items,
        generated_at=generated_at,
        output_path=HTML_OUTPUT_FILE,
        all_sources_failed=all_sources_failed,
    )

    if errors:
        with ERROR_LOG_FILE.open("a", encoding="utf-8") as fh:
            for err in errors:
                line = f"[{err['logged_at']}] {err['source']} ({err['url']}): {err['error']}\n"
                fh.write(line)
                print(f"Source failed: {line.strip()}")

    print(f"Wrote {len(items)} report items to: {OUTPUT_FILE}")
    print(f"Wrote HTML report to: {HTML_OUTPUT_FILE}")
    if errors:
        print(f"Logged {len(errors)} source failures to: {ERROR_LOG_FILE}")


if __name__ == "__main__":
    main()

