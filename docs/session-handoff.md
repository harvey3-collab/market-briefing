# Session Handoff

## Project Goal
Build a zero-cost, GitHub-based system that automatically generates a daily market briefing website.

## Current Implemented Modules
- `scripts/source_config.py`
  - Minimal free-source registry by market (`us`, `crypto`, `forex_macro`).
- `scripts/collector.py`
  - Fetches RSS/Atom feeds using Python standard library.
  - Logs per-source failures and continues.
- `scripts/normalizer.py`
  - Normalizes feed items into minimal `news_item` format.
  - Adds optional `related_assets` via keyword detection for US/crypto/forex_macro.
- `scripts/postprocess.py`
  - Filtering: required fields + market allowlist + recent time window.
  - Deduplication: basic title similarity + keyword overlap, keep newer item.
  - Ranking: simple rule priority (macro-like keywords -> core assets -> recency).
  - Final cap: top 10.
- `scripts/html_renderer.py`
  - Renders Traditional Chinese HTML report.
  - Groups sections in order: `us` -> `forex_macro` -> `crypto`.
  - Empty states:
    - `目前無重大事件`
    - `目前無可用資料`
  - Per-card rows: title link, source, published time (formatted), optional summary/assets.
- `scripts/run_collection.py`
  - Entry script that runs collection -> normalization -> postprocess -> JSON + HTML output.
- `.github/workflows/daily-report.yml`
  - Scheduled + manual workflow for report generation and GitHub Pages deployment.

## Current Markets Supported
- `us`
- `forex_macro`
- `crypto`

## Current Output Files
- `output/report_items.json`
- `output/report.html`
- `output/index.html` (generated in CI for Pages publish step)
- `output/collection_errors.log` (when source failures occur)

## Current GitHub Actions / Pages Status
- Workflow file exists: `.github/workflows/daily-report.yml`.
- Workflow includes checkout, Python setup, optional requirements install, report run, output verification, Pages artifact upload, deploy.
- Deploy currently blocked at repository-level Pages configuration.

## Current Blocker
- `actions/configure-pages` / `actions/deploy-pages` fails because GitHub Pages is not enabled/configured in repository settings yet.
- There is a Node.js 20 warning in workflow logs, but this is not the primary blocker.

## Exact Next Action
In the GitHub repository:
1. Go to `Settings -> Pages`.
2. Set `Build and deployment` source to `GitHub Actions`.
3. Save settings, then rerun workflow `Daily Market Report` from Actions tab.
