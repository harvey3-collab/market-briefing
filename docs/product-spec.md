# Product Spec: Zero-Cost Automated Market Briefing System

## Project
Zero-cost automated market briefing system.

## Goal
Build a GitHub-based system that automatically generates a daily market briefing website.

## Constraints
- No paid APIs in v1
- No OpenAI / Claude API in v1
- Use free data sources only
- Must be modular and upgradeable later
- Do not implement app logic yet
- Do not generate Python pipeline yet
- Do not generate GitHub Actions yet
- Only create the project foundation files

## Markets Priority
1. Taiwan stocks
2. US stocks
3. Forex
4. Crypto

## Core Assets

### Taiwan
- TSMC
- Hon Hai
- Delta
- MediaTek
- ETFs: 0050, 006208

### US
- NVDA
- AAPL
- MSFT
- AMZN
- META
- TSLA
- PLTR
- COHR
- ETFs: QQQ, SMH, SHLD

### Forex / Macro
- XAUUSD
- EURUSD
- GBPUSD
- USDJPY
- DXY
- FOMC
- CPI
- PPI
- NFP
- ISM
- central banks

### Crypto
- BTC
- ETH (must appear every day)

## Reports

### Morning Briefing
- Yesterday Taiwan market
- Last US session
- Macro events

### Evening Briefing
- 19:30 Taiwan time
- Taiwan market close summary
- US pre-market context
- Forex / Gold / Crypto

## Rules
- Max 10 items per report
- Deduplicate similar news
- Only show repeated news if there is new development
- If no major event, show "No major events"
- If a source fails, continue and log the error
- If summarization fails later, fallback to rule-based summary

## Out of Scope for This Phase
- Application/business logic implementation
- Data pipeline implementation
- GitHub Actions workflow implementation

## Initial Foundation Deliverables
- Project folder structure setup
- Repository operating rules (`AGENTS.md`)
- Product definition document (`docs/product-spec.md`)

## Deduplication Strategy (v1)
- Identify similar news by comparing titles (string similarity)
- If two items share similar keywords, keep only one
- Prefer the more detailed or more recent one
- Allow reappearance only if there is new development

## Ranking Logic (v1)
Rank importance using:
1. Macro events (FOMC, CPI, NFP, central banks)
2. Impacted core assets (TSMC, NVDA, BTC, etc.)
3. Market-wide impact (index-level, ETF-level)
4. Recency (more recent = higher priority)

Limit output to top 10 items.
