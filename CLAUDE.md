# LLM Wiki — Little Dot Studios BI

## Purpose
This wiki supports research and preparation for the Business Intelligence Analyst role at Little Dot Studios (Commercial Planning team, Los Angeles). It accumulates knowledge about the company, the industry, the role, and relevant analytical concepts.

## Directory Structure

```
raw/          # Source documents — immutable. Drop articles, PDFs, notes here.
wiki/         # LLM-generated markdown pages — you write and maintain these.
  index.md    # Catalog of all wiki pages with one-line summaries
  log.md      # Append-only log of ingests, queries, and lint passes
CLAUDE.md     # This file — schema and operating instructions
```

## Wiki Page Types

| Type | Naming | Purpose |
|---|---|---|
| Company | `company-*.md` | Pages about Little Dot Studios, its products, structure, clients |
| Industry | `industry-*.md` | YouTube ecosystem, digital media, content production trends |
| Role | `role-*.md` | BI Analyst responsibilities, skills, interview prep |
| Concept | `concept-*.md` | Analytical concepts: time tracking, resource planning, profitability, CRM |
| Source | `source-*.md` | Summary of a specific ingested source document |
| Synthesis | `synthesis-*.md` | Cross-cutting analyses, comparisons, evolving thesis pages |

## Workflows

### Ingest a source
1. Read the source document from `raw/`
2. Discuss key takeaways with the user
3. Write a `source-*.md` summary page in `wiki/`
4. Update relevant company, industry, role, or concept pages
5. Update `wiki/index.md` with new and modified pages
6. Append an entry to `wiki/log.md`: `## [YYYY-MM-DD] ingest | <title>`

### Answer a query
1. Read `wiki/index.md` to find relevant pages
2. Read the relevant pages
3. Synthesize an answer with citations to wiki pages
4. If the answer is valuable, offer to file it as a `synthesis-*.md` page
5. Append to `wiki/log.md`: `## [YYYY-MM-DD] query | <question>`

### Lint the wiki
1. Check for: contradictions, stale claims, orphan pages, missing cross-references, important concepts without their own page
2. Report findings and fix with user approval
3. Append to `wiki/log.md`: `## [YYYY-MM-DD] lint | <summary>`

## Conventions
- All pages use markdown
- Cross-references use standard markdown links: `[Page Title](filename.md)`
- Keep pages focused — one entity or concept per page
- Flag contradictions explicitly: > ⚠️ **Contradiction:** ...
- Flag gaps explicitly: > 📌 **Gap:** ...
