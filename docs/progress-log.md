# Progress Log

## Chronological Summary
1. **Repository foundation created**
- Base folders created: `docs/`, `data/`, `scripts/`, `output/`, `.github/workflows/`.
- `AGENTS.md` and `docs/product-spec.md` created with v1 constraints and guardrails.

2. **Foundation docs refined**
- Added explicit data constraints (free-only, no paid APIs in v1).
- Added output requirements (HTML + structured JSON).
- Added failure-handling rules and v1 dedup/ranking documentation.

3. **Minimal pipeline design completed**
- Defined end-to-end flow and module boundaries.
- Simplified to minimal viable architecture per v1 request.

4. **Minimal data prototype implemented**
- Added source loader, collector, normalizer, runnable entry script.
- Output JSON generated under `output/`.
- Source failures logged while pipeline continues.

5. **Postprocess slice added**
- Implemented filtering, simple deduplication, and simple rule-based ranking.
- Limited final output to top 10 items.
- Kept JSON schema stable.

6. **HTML report generation added**
- Added dedicated renderer module.
- Generated `output/report.html`.
- Added empty-state handling for no major events vs no data available.

7. **UI/report refinements**
- Converted report UI labels to Traditional Chinese.
- Grouped cards by market section with ordering.
- Removed per-card market row (market now represented by section).
- Formatted published time display to `YYYY-MM-DD HH:MM UTC` with fallback.
- Renamed JSON artifact to `output/report_items.json`.

8. **Market coverage extended**
- Added `forex_macro` market sources and keyword extraction support.
- Updated report section order to include `外匯與總經`.

9. **Automation/deployment added**
- Added GitHub Actions workflow `.github/workflows/daily-report.yml`.
- Workflow runs daily + manually, generates outputs, uploads/deploys Pages artifact.

## Important Design Decisions
- Keep v1 strict and simple: no paid APIs, no LLM APIs, no complex scoring.
- Preserve modular boundaries:
  - data/source config
  - collection
  - normalization
  - postprocessing
  - rendering
  - orchestration entry script
- Fail-open behavior for source errors (continue and log).
- Keep JSON output intentionally minimal and stable.
- Keep rendering logic isolated in `scripts/html_renderer.py`.

## Simplifications Made for v1
- Minimal `news_item` schema only.
- Simple deduplication (title similarity + keyword overlap), no clustering.
- Rule-based ranking only; no multi-score model.
- Limited markets in implementation phase to `us`, `forex_macro`, `crypto`.
- No app server, no database, no Docker, no external paid service.

## Known Risks / Technical Debt
- External RSS/feed endpoint reliability can vary over time.
- Current source set is intentionally small and may miss some major events.
- Parsing is generic RSS/Atom and may not handle every source-specific edge case.
- Time formatting/display is UTC-only in cards for now.
- No tests yet (unit/integration), so regressions may be caught late.
- Workflow depends on repository-level Pages settings and permissions.
- Node.js 20 warning appears in workflow logs (non-blocking currently).
