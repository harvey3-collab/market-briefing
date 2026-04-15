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
STATUS_FILE = OUTPUT_DIR / "collection_status.json"
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
    success_by_url = {result.source_url: result for result in collected}
    error_by_url = {str(err.get("url", "")): err for err in errors}
    source_status: list[Dict[str, object]] = []
    for src in sources:
        url = src["url"]
        if url in success_by_url:
            result = success_by_url[url]
            source_status.append(
                {
                    "name": src["name"],
                    "market": src["market"],
                    "url": url,
                    "status": "ok",
                    "raw_item_count": len(result.raw_items),
                }
            )
        else:
            err = error_by_url.get(url, {})
            source_status.append(
                {
                    "name": src["name"],
                    "market": src["market"],
                    "url": url,
                    "status": "failed",
                    "error": str(err.get("error", "unknown error")),
                }
            )

    source_success_count = sum(1 for row in source_status if row["status"] == "ok")
    source_failure_count = sum(1 for row in source_status if row["status"] == "failed")
    if source_success_count == 0:
        run_status = "all_sources_failed"
    elif source_failure_count > 0:
        run_status = "partial_source_failure"
    else:
        run_status = "ok"

    payload: Dict[str, object] = {
        "generated_at": generated_at,
        "item_count": len(items),
        "items": items,
        "run_status": run_status,
        "source_success_count": source_success_count,
        "source_failure_count": source_failure_count,
        "source_snapshot": [{"name": src["name"], "market": src["market"], "url": src["url"]} for src in sources],
    }
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    all_sources_failed = len(collected) == 0 and len(errors) > 0
    render_report_html(
        items=items,
        generated_at=generated_at,
        output_path=HTML_OUTPUT_FILE,
        all_sources_failed=all_sources_failed,
    )

    status_payload: Dict[str, object] = {
        "generated_at": generated_at,
        "run_status": run_status,
        "configured_source_count": len(sources),
        "source_success_count": source_success_count,
        "source_failure_count": source_failure_count,
        "sources": source_status,
    }
    STATUS_FILE.write_text(json.dumps(status_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Keep log entries scoped to the latest run to avoid stale confusion.
    ERROR_LOG_FILE.write_text("", encoding="utf-8")
    if errors:
        with ERROR_LOG_FILE.open("a", encoding="utf-8") as fh:
            for err in errors:
                line = f"[{err['logged_at']}] {err['source']} ({err['url']}): {err['error']}\n"
                fh.write(line)
                print(f"Source failed: {line.strip()}")

    print(f"Wrote {len(items)} report items to: {OUTPUT_FILE}")
    print(f"Wrote HTML report to: {HTML_OUTPUT_FILE}")
    print(f"Wrote collection status to: {STATUS_FILE}")
    print(
        "Source summary: "
        f"{source_success_count} succeeded, "
        f"{source_failure_count} failed, "
        f"run_status={run_status}"
    )
    if errors:
        print(f"Logged {len(errors)} source failures to: {ERROR_LOG_FILE}")


if __name__ == "__main__":
    main()

