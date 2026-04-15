Project: market-briefing

Goal:
Generate a daily automated financial market briefing website using GitHub Actions.

Current Status:
- GitHub Actions runs successfully
- GitHub Pages deployed successfully
- HTML page renders correctly

Structure:
- scripts/
  - pipeline (data collection + processing)
  - html_renderer.py (UI layer)
- output/
- docs/
- .github/workflows/daily-report.yml

Current Problems:
1. UI looks like developer output (too basic)
2. Content mostly English (poor readability)
3. No summarization layer (just RSS dump)

Development Strategy:
- DO NOT change workflow or deployment
- DO NOT break pipeline
- Improve step-by-step:

Step 1: Improve UI (html_renderer)
Step 2: Add Chinese summarization
Step 3: Improve content quality/filtering