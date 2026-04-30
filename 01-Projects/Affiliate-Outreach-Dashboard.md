# Affiliate Outreach Dashboard

**Owner:** Barron Zuo — Cell Digital Technology Inc.
**Last refresh:** 2026-04-22
**Sync repo:** [CitizenZM/affiliate-outreach-sync](https://github.com/CitizenZM/affiliate-outreach-sync)

---

## Live Programs

| # | Program | Platform | Region | Ledger size | Emails captured | Last activity | Status |
|---|---|---|---|---:|---:|---|---|
| 1 | **TCL** | Impact (48321) | US | **996** | 572 (57.4%) | 2026-04-21 | ✅ 1000-proposal sprint complete |
| 2 | **Rockbros** | Awin | EU | **1,205** | 507 (42.1%) | 2026-04-20 | 🟢 Active — next batch pending |
| 3 | **Rockbros** | Awin | US | **859** | 859 (100%) | 2026-04-20 | 🟢 Active — email-captured |
| 4 | **Oufer Jewelry** | Awin | US | **777** | 1 (<1%) | 2026-04-17 | 🟡 Email capture needs fix |
| 5 | **Ottocast** | Impact | US | — | — | not yet launched | ⏳ Setup ready |

## Artifacts

| Program | Ledger | Latest Report | Skill |
|---|---|---|---|
| TCL US | [[Impact-TCL-US-Outreach-Ledger]] | [[Impact-TCL-US-Outreach-Report-2026-04-21]] | `impact-tcl-us-outreach` |
| Rockbros EU | [[Awin-Rockbros-EU-Outreach-Ledger]] | [[Awin-Rockbros-EU-Outreach-Report-2026-04-15]] | `awin-rockbros-eu-outreach` |
| Rockbros US | [[Awin-Rockbros-US-Outreach-Ledger]] | [[Awin-Rockbros-Outreach-Report-2026-04-15]] | `awin-rockbros-us-outreach` |
| Oufer US | [[Awin-Oufer-US-Outreach-Ledger]] | [[Awin-Oufer-US-Outreach-Report-2026-04-15]] | `awin-oufer-us-outreach` |
| Ottocast US | — | — | `impact-ottocast-outreach` |

## Weekly Report Skills

- `awin-rockbros-weekly-report` — pushes to `affiliate-weekly-reports` GitHub repo + Vercel
- `awin-oufer-us-weekly-report` — forked from Rockbros, US-only cut
- `impact-tcl-us-weekly-report` — TCL performance cut

## Priority Queue

1. **Oufer US email capture** — ledger shows 1/777 captured; diagnose selector in detail page
2. **Rockbros EU follow-up** — T+10 nudge for 507 email-captured publishers
3. **TCL US reply triage** — T+3 from 2026-04-21 = 2026-04-24; monitor Impact inbox
4. **Ottocast US kickoff** — run `/impact-ottocast-setup`, then first 100-proposal batch
5. **Weekly reports** — run all three weekly report skills this Sunday

## Ops Notes

- Contract date = tomorrow at runtime (never hardcoded)
- Terms (5% Standard Publisher) verified before every Impact send
- Publisher emails **never** leak into external Word/PDF/HTML reports — mask or omit
- Syncing: `./sync-obsidian.sh push` after any ledger update
