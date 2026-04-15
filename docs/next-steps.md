# Next Steps

## Immediate Next Step
Enable GitHub Pages at repository level, then rerun the existing workflow.

1. Open repository `Settings -> Pages`.
2. Set `Build and deployment` to `GitHub Actions`.
3. Save.
4. Go to `Actions -> Daily Market Report` and rerun the latest run.
5. Confirm deployment succeeds and `page_url` is available.

## After-That Roadmap
1. **Deployment verification**
- Confirm live site loads and shows generated report.
- Confirm `report_items.json` is accessible from Pages artifact.

2. **Operational hardening (still simple)**
- Add a small `requirements.txt` only if needed by future dependencies.
- Add lightweight run metadata in logs (counts by market, source success/failure).

3. **Data quality improvements**
- Review current feeds periodically for availability and relevance.
- Tune keyword lists for `forex_macro` and asset detection.

4. **Testing baseline**
- Add minimal tests for:
  - datetime parsing/formatting fallback
  - dedup/ranking deterministic behavior
  - renderer empty-state behavior

## Explicitly NOT To Do Yet
- Do not introduce paid APIs.
- Do not add OpenAI/Claude API usage.
- Do not redesign current data logic architecture.
- Do not add GitHub Actions complexity beyond current workflow.
- Do not build backend services, database, or Docker stack.
- Do not add Taiwan market ingestion yet unless requested next.
