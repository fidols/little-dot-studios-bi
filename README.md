# Little Dot Studios BI — LLM Wiki

A personal knowledge base for researching the Business Intelligence Analyst role at Little Dot Studios, built using the LLM Wiki pattern.

## Structure

```
raw/      # Source documents (articles, PDFs, notes) — immutable
wiki/     # LLM-maintained knowledge pages
CLAUDE.md # Schema and operating instructions for the LLM
```

## Wiki Pages

| Page | Type |
|---|---|
| [Little Dot Studios](wiki/company-little-dot-studios.md) | Company |
| [YouTube Ecosystem](wiki/industry-youtube-ecosystem.md) | Industry |
| [Digital Media Landscape](wiki/industry-digital-media-landscape.md) | Industry |
| [BI Analyst Role](wiki/role-bi-analyst.md) | Role |
| [Time Tracking Analytics](wiki/concept-time-tracking.md) | Concept |
| [Profitability Analysis](wiki/concept-profitability.md) | Concept |
| [Resource & Capacity Planning](wiki/concept-resource-planning.md) | Concept |
| [CRM Analytics](wiki/concept-crm-analytics.md) | Concept |

## How to Use

1. Drop source articles/documents into `raw/`
2. Tell Claude to ingest them — it will update the wiki automatically
3. Ask questions — Claude will search the wiki and synthesize answers
4. Periodically run a lint pass to keep the wiki healthy
