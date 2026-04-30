---
tags: [project, plan, affiliate, publisher-intel]
status: planning
priority: high
created: 2026-04-06
---
# Publisher Intelligence System — Master Plan

## Objective
Build a unified publisher CRM that consolidates all existing data, auto-enriches contacts, and tracks all email communications — replacing manual spreadsheets with a queryable, AI-enhanced database.

## Current State Audit

### Data Sources Already Available

| Source | Records | Data Type | Format |
|---|---|---|---|
| Captive8 Full Export | ~240K-2.4M | Publisher performance, audience | 48 XLSX files |
| Impact EmailLists | ~500+ | First Name, Last Name, Email, Company, Account ID | CSV (multiple brand exports) |
| Editor Contacts | ~50+ | Publisher, Editor Name, Title, Email, Website | XLSX |
| Media Kit Y2025 | 109 partners | Rate cards, placement fees, onboarding docs | PDF directories |
| AI Outreach Master | ~200+ | TikTok creators, emails, outreach status, AI drafts | CSV |
| Publisher Template | schema | Name, email, website, socials, type, tier, niche | CSV |
| Benchmark Overview | ~27 files | ROAS, CVR, revenue contribution by partner | CSV |
| Publisher Performance | multiple | Per-brand performance (TCL, Sweetnight, Segway, etc.) | CSV |
| Recommended Partners | ~80+ | Impact recommended partners | CSV |
| Paid Placement Opps | list | 2026 managed publisher placement opportunities | XLSX |

### Supabase Schema Already Built (izeixnkpquztaczehhum)

| Table | Rows | Key Columns |
|---|---|---|
| `publishers` | 0 | 40+ cols: name, domain, contact_email, contact_name, tier, GMV, ROI, CVR, enrichment |
| `publisher_editors` | 41 | editor_name, role, email, linkedin_url, twitter_handle, recent articles |
| `email_logs` | 0 | publisher_id, to_email, subject, body, status, resend_id, sent_at |
| `enrichment_log` | 5 | publisher_id, source, fields_updated, status |
| `brand_coverage` | 50 | publisher_id, brand_name, article_title, article_url, sentiment |
| `recommendation_runs` | 0 | brief_json, result_json, top_categories, suggested_cpa |

**Bottom line: Schema is ready. Tables are empty. Data exists in files but hasn't been imported.**

---

## Phase 1: Data Consolidation (Week 1)
> Goal: Import all existing publisher data into Supabase `publishers` table

### 1.1 Import Impact EmailLists
- Parse all `*_EmailList.csv` files (TCL, Flybird, Yousuda, TotenCarry, FED, etc.)
- Deduplicate by email + company
- Map to publishers table: `contact_name`, `contact_email`, `publisher_name`, `affiliate_network = "Impact"`

### 1.2 Import Editor Contacts
- Parse `editor_contacts (1).xlsx`
- Load into `publisher_editors` (already has 41 rows — merge, don't replace)
- Link to parent publisher record

### 1.3 Import Benchmark Performance Data
- Parse all 27 Benchmark CSVs
- Map to publisher historical metrics: `historical_gmv`, `historical_clicks`, `historical_roi`, `historical_cvr`

### 1.4 Import Publisher Performance CSVs
- Per-brand files (sweetnight, gyroor, segway, etc.)
- Aggregate per-publisher across brands

### 1.5 Import Media Kit Directory
- Parse 109 partner folder names → create publisher records
- Store folder path as reference for manual media kit lookup
- Extract key terms from PDF filenames (rate card, BFCM, placement)

### 1.6 Import AI Outreach Data
- Parse `ai_outreach_master_ready.csv`
- Map TikTok creators into publishers with type = "creator"
- Preserve outreach status, AI drafts, priority tier

### 1.7 Import Captive8 Data (Big Lift)
- Sample 2-3 XLSX files to understand schema
- Build import script to extract publisher profiles
- Merge with existing records by domain/name matching

### Deliverable
- **~500-1000+ unique publisher records** in Supabase
- **~100+ editor contacts** linked to publishers
- **All historical performance** metrics populated

---

## Phase 2: Contact Enrichment (Week 2)
> Goal: Fill gaps in contact names, emails, LinkedIn profiles

### 2.1 Domain-Based Enrichment
- For publishers with `website` but no `contact_email`:
  - Scrape common patterns: info@, press@, partnerships@, advertising@
  - Check LinkedIn company page for affiliate/partnership managers

### 2.2 AI-Powered Contact Discovery
- Use Exa/web search to find:
  - "{publisher_name} affiliate manager email"
  - "{publisher_name} partnerships contact"
  - LinkedIn profiles of ad/affiliate team members

### 2.3 Impact API Enrichment
- Pull latest publisher data from Impact API (if API access available)
- Update performance metrics, status, and contact info

### 2.4 Enrichment Tracking
- Log all enrichment runs in `enrichment_log` table
- Track: source, fields_updated, confidence score

### Deliverable
- **80%+ publishers have contact_email**
- **60%+ have contact_name**
- **All enrichment attempts logged**

---

## Phase 3: Email Communication Tracking (Week 3)
> Goal: Track all publisher communications in one place

### 3.1 Gmail Integration
- Use Gmail MCP to scan sent/received emails matching publisher domains
- Parse: date, subject, body preview, thread_id
- Store in `email_logs` table linked to publisher_id

### 3.2 Outreach Pipeline
- Status tracking: `not_contacted` → `email_sent` → `replied` → `negotiating` → `active` → `churned`
- Template system for common outreach types:
  - Cold intro
  - Rate card request
  - Performance review
  - BFCM/seasonal pitch
  - Reactivation

### 3.3 Follow-Up Automation
- Flag publishers with no response after 5 days
- Generate follow-up drafts using AI
- Track follow-up count and next follow-up date

### Deliverable
- **All historical email comms linked to publishers**
- **Outreach pipeline with status tracking**
- **AI-generated follow-up drafts**

---

## Phase 4: Intelligence Dashboard (Week 4)
> Goal: Queryable dashboard for publisher decisions

### 4.1 Obsidian Dataview Queries
- Top publishers by GMV
- Publishers needing follow-up
- Publishers by tier/category
- Recently contacted vs. cold
- Enrichment gaps to fill

### 4.2 Publisher Scoring Model
- Composite score: performance (40%) + engagement (30%) + potential (30%)
- Auto-tier: T1 (>1M MAU), T2 (100K-1M), T3 (<100K)
- Flag high-potential publishers not yet contacted

### 4.3 Obsidian Publisher Notes
- Auto-generate Obsidian note per top-50 publisher
- Include: contact info, performance summary, email history, media kit link
- Bi-directional links to brand notes and campaign notes

### Deliverable
- **Live dashboard in Obsidian + Supabase**
- **Publisher scoring and auto-tiering**
- **Per-publisher intelligence notes**

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Obsidian Vault                  │
│  05-Project-Status/  06-Publishers/         │
│  Dataview queries ← frontmatter metadata    │
└──────────────────┬──────────────────────────┘
                   │ read/write markdown
                   │
┌──────────────────┴──────────────────────────┐
│            Claude Code CLI                   │
│  Import scripts │ Enrichment │ AI drafts    │
└──────────────────┬──────────────────────────┘
                   │ SQL via MCP
                   │
┌──────────────────┴──────────────────────────┐
│         Supabase (izeixnkpquztaczehhum)     │
│  publishers │ publisher_editors │ email_logs │
│  enrichment_log │ brand_coverage            │
└──────────────────┬──────────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
  Gmail MCP    Impact API    Exa Search
  (comms)      (metrics)    (enrichment)
```

## Data Model (Supabase — already exists)

```sql
-- Core: publishers (40+ columns, ready to use)
-- Contacts: publisher_editors (linked via publisher_id)
-- Comms: email_logs (linked via publisher_id)
-- Tracking: enrichment_log (audit trail)
-- Coverage: brand_coverage (what they've written about)
```

## Priority Order

1. **Phase 1.1-1.2** — Import Impact emails + editor contacts (highest ROI, fastest)
2. **Phase 1.5** — Import 109 media kit partners (already named, just need records)
3. **Phase 3.1** — Gmail scan (immediate visibility into past comms)
4. **Phase 1.3-1.4** — Performance data import (enriches existing records)
5. **Phase 2** — Enrichment (fills gaps)
6. **Phase 4** — Dashboard (visualizes everything)

## Next Step
Start Phase 1.1: Import all Impact EmailList CSVs into Supabase `publishers` table.
