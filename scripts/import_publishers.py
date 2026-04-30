#!/usr/bin/env python3
"""
Phase 1: Import all publisher data into consolidated CSV for Supabase import.
Deduplicates by company name + email across all sources.
Outputs SQL INSERT statements for direct execution.
"""

import pandas as pd
import os
import json
import re
from pathlib import Path

BASE = "/Volumes/workssd/New Download"
OUTPUT_DIR = "/Volumes/workssd/ObsidianVault/scripts/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 1. Import all Impact EmailLists
# ============================================================
print("=== Phase 1.1: Impact EmailLists ===")

email_files = [
    f"{BASE}/Impact_EmailList.csv",
    f"{BASE}/Flybird Impact_EmailList.csv",
    f"{BASE}/Yousuda Impact_EmailList.csv",
    f"{BASE}/FED Impact_EmailList.csv",
    f"{BASE}/TotenCarry Impact_EmailList.csv",
]

email_dfs = []
for f in email_files:
    if os.path.exists(f):
        brand = Path(f).stem.replace(" Impact_EmailList", "").replace("Impact_EmailList", "General")
        df = pd.read_csv(f)
        df.columns = [c.strip() for c in df.columns]
        df["source_brand"] = brand
        df["source_file"] = Path(f).name
        email_dfs.append(df)
        print(f"  Loaded {len(df)} rows from {Path(f).name}")

emails_all = pd.concat(email_dfs, ignore_index=True)
print(f"  Total raw: {len(emails_all)} rows")

# Deduplicate by Email + Company
emails_deduped = emails_all.drop_duplicates(subset=["Email", "Company"], keep="first")
print(f"  After dedup: {len(emails_deduped)} unique email+company combos")

# Build publisher records from emails
email_publishers = []
for _, row in emails_deduped.iterrows():
    first = str(row.get("First Name", "")).strip()
    last = str(row.get("Last Name", "")).strip()
    contact_name = f"{first} {last}".strip()
    if contact_name == "nan nan" or contact_name == "nan":
        contact_name = None

    email = str(row.get("Email", "")).strip()
    if email == "nan":
        email = None

    company = str(row.get("Company", "")).strip()
    if company == "nan":
        company = None

    partner_type = str(row.get("Partner Type", "")).strip()
    if partner_type == "nan":
        partner_type = None

    account_id = row.get("Account Id")

    email_publishers.append({
        "publisher_name": company,
        "contact_name": contact_name,
        "contact_email": email,
        "affiliate_network": "Impact",
        "affiliate_type": partner_type,
        "summary_note": f"Impact Account ID: {account_id}" if pd.notna(account_id) else None,
    })

df_email_pub = pd.DataFrame(email_publishers)
df_email_pub = df_email_pub[df_email_pub["publisher_name"].notna()]
# Deduplicate by publisher name, keep the one with most data
df_email_pub = df_email_pub.drop_duplicates(subset=["publisher_name", "contact_email"], keep="first")
print(f"  Unique publishers from EmailLists: {len(df_email_pub)}")

# ============================================================
# 2. Import Editor Contacts
# ============================================================
print("\n=== Phase 1.2: Editor Contacts ===")

editor_file = f"{BASE}/editor_contacts (1).xlsx"
if os.path.exists(editor_file):
    df_editors = pd.read_excel(editor_file)
    df_editors.columns = [c.strip() for c in df_editors.columns]
    print(f"  Loaded {len(df_editors)} editor contacts")
    print(f"  Columns: {list(df_editors.columns)}")
else:
    df_editors = pd.DataFrame()
    print("  Editor file not found")

# ============================================================
# 3. Import Performance Data
# ============================================================
print("\n=== Phase 1.3: Performance Data ===")

perf_files_awin = [
    (f"{BASE}/sweetnight 2025 99625-publisher-performance.csv", "Sweetnight"),
    (f"{BASE}/gyroor 93237-publisher-performance.csv", "Gyroor"),
    (f"{BASE}/Segway 93539-publisher-performance.csv", "Segway"),
    (f"{BASE}/bagsmart 28621-publisher-performance.csv", "Bagsmart"),
]

perf_files_impact = [
    (f"{BASE}/4916-PerformancebyPartner.csv", "TCL-Impact"),
    (f"{BASE}/4916-PerformancebyPartner (1).csv", "TCL-Impact-2"),
    (f"{BASE}/4916-PerformancebyPartner-2.csv", "TCL-Impact-3"),
    (f"{BASE}/4916-PerformancebyPartner-3.csv", "TCL-Impact-4"),
    (f"{BASE}/TotenCarry4916-PerformancebyPartner.csv", "TotenCarry-Impact"),
]

perf_records = []

# Awin format
for fpath, brand in perf_files_awin:
    if os.path.exists(fpath):
        df = pd.read_csv(fpath)
        df.columns = [c.strip().strip('"') for c in df.columns]
        for _, row in df.iterrows():
            name = str(row.get("publisher_name", "")).strip().strip('"')
            if name and name != "nan":
                revenue = row.get("total_revenue", 0)
                transactions = row.get("total_transactions", 0)
                clicks = row.get("all_clicks", 0)
                roi = row.get("return_on_investment (ROI)", 0)
                cvr = row.get("total_conversion_rate", 0)
                try:
                    revenue = float(str(revenue).strip('"'))
                except:
                    revenue = 0
                try:
                    transactions = int(float(str(transactions).strip('"')))
                except:
                    transactions = 0
                try:
                    clicks = int(float(str(clicks).strip('"')))
                except:
                    clicks = 0
                try:
                    roi = float(str(roi).strip('"'))
                except:
                    roi = 0
                try:
                    cvr = float(str(cvr).strip('"'))
                except:
                    cvr = 0
                perf_records.append({
                    "publisher_name": name,
                    "brand": brand,
                    "network": "Awin",
                    "revenue": revenue,
                    "transactions": transactions,
                    "clicks": clicks,
                    "roi": roi,
                    "cvr": cvr,
                })
        print(f"  {brand}: {len(df)} publishers")

# Impact format
for fpath, brand in perf_files_impact:
    if os.path.exists(fpath):
        df = pd.read_csv(fpath)
        df.columns = [c.strip() for c in df.columns]
        for _, row in df.iterrows():
            name = str(row.get("Partner", "")).strip()
            if name and name != "nan":
                revenue = row.get("Revenue", 0)
                clicks = row.get("Clicks", 0)
                actions = row.get("Actions", 0)
                try:
                    revenue = float(revenue)
                except:
                    revenue = 0
                try:
                    clicks = int(float(clicks))
                except:
                    clicks = 0
                try:
                    actions = int(float(actions))
                except:
                    actions = 0
                perf_records.append({
                    "publisher_name": name,
                    "brand": brand,
                    "network": "Impact",
                    "revenue": revenue,
                    "transactions": actions,
                    "clicks": clicks,
                    "roi": 0,
                    "cvr": (actions / clicks * 100) if clicks > 0 else 0,
                })
        print(f"  {brand}: {len(df)} publishers")

df_perf = pd.DataFrame(perf_records)
if len(df_perf) > 0:
    # Aggregate performance per publisher (sum across brands)
    perf_agg = df_perf.groupby("publisher_name").agg({
        "revenue": "sum",
        "transactions": "sum",
        "clicks": "sum",
    }).reset_index()
    perf_agg["roi"] = perf_agg.apply(lambda r: r["revenue"] / max(r["transactions"], 1), axis=1)
    perf_agg["cvr"] = perf_agg.apply(lambda r: r["transactions"] / max(r["clicks"], 1) * 100, axis=1)
    print(f"  Unique publishers with performance data: {len(perf_agg)}")
else:
    perf_agg = pd.DataFrame()

# ============================================================
# 4. Import Media Kit Partners (109)
# ============================================================
print("\n=== Phase 1.5: Media Kit Partners ===")

media_kit_dir = f"{BASE}/[Internal ]  - Media Kit Y2025"
media_kit_partners = []
if os.path.exists(media_kit_dir):
    for folder in sorted(os.listdir(media_kit_dir)):
        if not folder.startswith("."):
            media_kit_partners.append(folder)
    print(f"  Found {len(media_kit_partners)} media kit partners")

# ============================================================
# 5. Import AI Outreach Creators
# ============================================================
print("\n=== Phase 1.6: AI Outreach Creators ===")

outreach_file = f"{BASE}/ai_outreach_master_ready.csv"
outreach_records = []
if os.path.exists(outreach_file):
    df_out = pd.read_csv(outreach_file)
    for _, row in df_out.iterrows():
        handle = str(row.get("tiktok_handle", "")).strip()
        email = str(row.get("contact_email_x", "")).strip()
        if handle and handle != "nan":
            outreach_records.append({
                "publisher_name": handle,
                "contact_email": email if email != "nan" and email else None,
                "affiliate_type": "Creator",
                "category": str(row.get("niche_guess", "")).strip() if str(row.get("niche_guess", "")) != "nan" else None,
                "summary_note": f"TikTok: {row.get('tiktok_url_x', '')}",
            })
    print(f"  Loaded {len(outreach_records)} creators")

# ============================================================
# 6. MERGE all sources into one master list
# ============================================================
print("\n=== Merging all sources ===")

master = {}

def add_or_merge(name, data, source):
    """Merge publisher data by normalized name."""
    key = name.lower().strip()
    if not key or key == "nan":
        return
    if key not in master:
        master[key] = {
            "publisher_name": name.strip(),
            "contact_email": None,
            "contact_name": None,
            "affiliate_network": None,
            "affiliate_type": None,
            "category": None,
            "historical_gmv": None,
            "historical_transactions": None,
            "historical_clicks": None,
            "historical_roi": None,
            "historical_cvr": None,
            "summary_note": None,
            "gmv_history_source": None,
        }
    rec = master[key]
    for field in ["contact_email", "contact_name", "affiliate_network", "affiliate_type", "category", "summary_note"]:
        if data.get(field) and not rec.get(field):
            rec[field] = data[field]
    # Performance: keep highest
    for field in ["historical_gmv", "historical_transactions", "historical_clicks"]:
        if data.get(field):
            old = rec.get(field) or 0
            rec[field] = max(old, data[field])
    for field in ["historical_roi", "historical_cvr"]:
        if data.get(field) and data[field] > 0:
            rec[field] = data[field]
    if source and not rec.get("gmv_history_source"):
        rec["gmv_history_source"] = source

# Add email publishers
for _, row in df_email_pub.iterrows():
    add_or_merge(row["publisher_name"], row.to_dict(), "Impact EmailList")

# Add media kit partners
for partner in media_kit_partners:
    add_or_merge(partner, {"affiliate_type": "Managed Publisher"}, "Media Kit Y2025")

# Add performance data
if len(perf_agg) > 0:
    for _, row in perf_agg.iterrows():
        add_or_merge(row["publisher_name"], {
            "historical_gmv": row["revenue"],
            "historical_transactions": int(row["transactions"]),
            "historical_clicks": int(row["clicks"]),
            "historical_roi": row["roi"],
            "historical_cvr": row["cvr"],
        }, "Performance CSV")

# Add outreach creators
for rec in outreach_records:
    add_or_merge(rec["publisher_name"], rec, "AI Outreach")

# ============================================================
# 7. Output
# ============================================================
master_list = sorted(master.values(), key=lambda x: -(x.get("historical_gmv") or 0))
print(f"\n=== TOTAL UNIQUE PUBLISHERS: {len(master_list)} ===")

# Count stats
has_email = sum(1 for r in master_list if r.get("contact_email"))
has_name = sum(1 for r in master_list if r.get("contact_name"))
has_gmv = sum(1 for r in master_list if r.get("historical_gmv") and r["historical_gmv"] > 0)
print(f"  With email: {has_email}")
print(f"  With contact name: {has_name}")
print(f"  With GMV data: {has_gmv}")

# Output as JSON for SQL generation
output_path = f"{OUTPUT_DIR}/publishers_master.json"
with open(output_path, "w") as f:
    json.dump(master_list, f, indent=2, default=str)
print(f"\nSaved to {output_path}")

# Output SQL batches (100 per batch)
def escape_sql(val):
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        if pd.isna(val):
            return "NULL"
        return str(val)
    s = str(val).replace("'", "''")
    return f"'{s}'"

batch_size = 100
sql_files = []
for i in range(0, len(master_list), batch_size):
    batch = master_list[i:i+batch_size]
    values = []
    for r in batch:
        vals = ", ".join([
            escape_sql(r.get("publisher_name")),
            escape_sql(r.get("contact_email")),
            escape_sql(r.get("contact_name")),
            escape_sql(r.get("affiliate_network")),
            escape_sql(r.get("affiliate_type")),
            escape_sql(r.get("category")),
            escape_sql(r.get("historical_gmv")),
            escape_sql(r.get("historical_transactions")),
            escape_sql(r.get("historical_clicks")),
            escape_sql(r.get("historical_roi")),
            escape_sql(r.get("historical_cvr")),
            escape_sql(r.get("gmv_history_source")),
            escape_sql(r.get("summary_note")),
        ])
        values.append(f"({vals})")

    joined_values = ',\n'.join(values)
    sql = f"""INSERT INTO publishers (publisher_name, contact_email, contact_name, affiliate_network, affiliate_type, category, historical_gmv, historical_transactions, historical_clicks, historical_roi, historical_cvr, gmv_history_source, summary_note)
VALUES
{joined_values}
ON CONFLICT DO NOTHING;"""

    batch_num = i // batch_size + 1
    sql_path = f"{OUTPUT_DIR}/batch_{batch_num:03d}.sql"
    with open(sql_path, "w") as f:
        f.write(sql)
    sql_files.append(sql_path)

print(f"Generated {len(sql_files)} SQL batch files")

# Also generate editor SQL
if len(df_editors) > 0:
    editor_values = []
    for _, row in df_editors.iterrows():
        pub = str(row.get("Publisher", "")).strip()
        name = str(row.get("Editor Name", "")).strip()
        role = str(row.get("Title", "")).strip()
        email = str(row.get("Email", "")).strip()
        website = str(row.get("Website", "")).strip()
        notes = str(row.get("Notes", "")).strip()

        for val in [pub, name]:
            if val == "nan":
                continue

        editor_values.append(f"({escape_sql(pub)}, {escape_sql(name if name != 'nan' else None)}, {escape_sql(role if role != 'nan' else None)}, {escape_sql(email if email != 'nan' else None)}, {escape_sql(website if website != 'nan' else None)}, {escape_sql(notes if notes != 'nan' else None)})")

    joined_editor_values = ',\n'.join(editor_values)
    editor_sql = f"""-- Editor contacts: link to publishers after import
-- Will need publisher_id lookup
INSERT INTO publisher_editors (publisher_id, editor_name, role, email, bio, recent_article_url)
SELECT p.id, e.editor_name, e.role, e.email, e.notes, e.website
FROM (VALUES
{joined_editor_values}
) AS e(publisher_name, editor_name, role, email, website, notes)
JOIN publishers p ON LOWER(p.publisher_name) = LOWER(e.publisher_name);"""

    editor_path = f"{OUTPUT_DIR}/editors_import.sql"
    with open(editor_path, "w") as f:
        f.write(editor_sql)
    print(f"Generated editor import SQL: {editor_path}")

print("\n=== DONE ===")
