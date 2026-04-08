# AGENTS

## Repository Development Rules

1. Step-by-step development only. Implement in small, verifiable increments.
2. No over-engineering. Favor simple, direct solutions over complex abstractions.
3. Do not build unrequested features. Stay strictly within explicitly requested scope.
4. Follow `docs/product-spec.md` strictly as the source of product requirements.
5. Prefer clarity and maintainability in structure, naming, and documentation.
6. Keep future upgradeability in mind by preserving modular boundaries.

## Current Scope Guardrails

- This repository is currently in foundation phase only.
- Do not implement app logic yet.
- Do not generate Python pipeline yet.
- Do not generate GitHub Actions yet.
- Only create and refine project foundation files unless explicitly requested otherwise.

## Data Constraints

- Only use free data sources (RSS, public endpoints, simple scraping)
- Do not introduce paid APIs under any condition in v1

## Output Requirements

- Must generate HTML output
- Should also prepare structured JSON output for future use
- Keep output simple and readable

## Failure Handling Rules

- If a data source fails, continue processing other sources
- If all sources fail, still generate a report with "No data available"
- If no major events, output "No major events"
- Do not stop the pipeline due to partial failure

## Change Discipline

- Each task should state what is included and what is excluded.
- Keep changes minimal and reversible.
- Update documentation before implementation when requirements evolve.
- If requirements conflict, resolve in favor of `docs/product-spec.md` and latest explicit user instruction.
