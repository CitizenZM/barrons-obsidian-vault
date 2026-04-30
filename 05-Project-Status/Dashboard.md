# Project Dashboard

> Last updated: 2026-04-07

## Active Plans
- [[Publisher-Intelligence-System]] — Unified publisher CRM with contact enrichment + email tracking

## Active Dev Projects

| Project | Stack | GitHub | Status | Priority |
|---|---|---|---|---|
| [[openclaw]] | Python agent system | [repo](https://github.com/CitizenZM/openclaw) | Active — swarm agents, model routing | High |
| [[xark-ai]] | Next.js + Supabase | [repo](https://github.com/CitizenZM/Ai) | Active — multi-brand workflow | High |
| [[affiliate-growth-intelligence]] | Next.js | [repo](https://github.com/CitizenZM/affiliate-growth-intelligence) | Rebranded to Xark OS | Medium |
| [[contentforge-ai]] | Next.js | [repo](https://github.com/CitizenZM/contentforge-ai) | Initial scaffold | Medium |
| [[mindbond]] | App | [repo](https://github.com/CitizenZM/mindbond) | Therapy app + SOPs | Medium |
| [[affiliate-audit-dashboard]] | Next.js | [repo](https://github.com/CitizenZM/affiliate-audit-dashboard) | AI system built, cleaned up | Medium |
| [[seo-dashboard-codex]] | Dashboard | [repo](https://github.com/CitizenZM/seo-dashboard-codex) | SEO audit SaaS | Low |
| [[growth-os]] | Mediabuy planning | [repo](https://github.com/CitizenZM/growth-os) | Growth OS | Low |
| [[aff-search-database]] | Publisher dashboard | [repo](https://github.com/CitizenZM/aff-search-database) | Design system started | Low |
| [[linkedin-job-apply]] | Python bot | [repo](https://github.com/CitizenZM/linkedin-job-apply) | Automation bot | Low |
| [[video-gen-ai]] | Frontend | [repo](https://github.com/CitizenZM/video-gen-ai) | Frontend reference | Low |
| [[ads-ai-gen]] | App | [repo](https://github.com/CitizenZM/ads-ai-gen) | Brand form app | Low |

## Local Projects (~/Projects)

| Project | Path | GitHub | Status |
|---|---|---|---|
| [[deer-flow]] | `~/Projects/deer-flow` | [fork](https://github.com/CitizenZM/deer-flow) / [upstream](https://github.com/bytedance/deer-flow) | Forked — custom agent events |
| [[mk-shopify]] | `~/Projects/mk-shopify` | [repo](https://github.com/CitizenZM/mk-shopify) | Shopify project |

## Key Paths

- **workssd**: `/Volumes/workssd/`
- **Obsidian Vault**: `/Volumes/workssd/ObsidianVault/`
- **Local Projects**: `~/Projects/`
- **Claude Config**: `~/.claude/`
- **Openclaw**: `/Volumes/workssd/openclaw/`

## Dataview Queries

### All Projects by Priority
```dataview
TABLE status, priority, stack, github AS "GitHub"
FROM "05-Project-Status"
WHERE contains(tags, "project")
SORT choice(priority = "high", 1, choice(priority = "medium", 2, 3)) ASC
```

### Active Projects Only
```dataview
TABLE stack, github AS "GitHub"
FROM "05-Project-Status"
WHERE status = "active"
SORT file.name ASC
```

### Projects Needing Attention
```dataview
LIST
FROM "05-Project-Status"
WHERE status = "needs-cleanup" OR status = "scaffold" OR status = "setup" OR status = "prototype"
```

### Projects by Tag
```dataview
TABLE tags, status, stack
FROM "05-Project-Status"
WHERE contains(tags, "affiliate")
```
