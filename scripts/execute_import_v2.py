#!/usr/bin/env python3
"""Execute publisher import via Supabase REST API - all keys normalized."""

import json
import urllib.request
import ssl
import time

SUPABASE_URL = "https://izeixnkpquztaczehhum.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6ZWl4bmtwcXV6dGFjemVoaHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE2OTc3NzYsImV4cCI6MjA4NzI3Mzc3Nn0.Z2gk7lLoE3zQJQr2W4Em0A5w68r0JeqDBMcJJEW3A-U"

ALL_KEYS = [
    "publisher_name", "contact_email", "contact_name",
    "affiliate_network", "affiliate_type", "category",
    "historical_gmv", "historical_transactions", "historical_clicks",
    "historical_roi", "historical_cvr", "gmv_history_source", "summary_note"
]

with open("/Volumes/workssd/ObsidianVault/scripts/output/publishers_master.json") as f:
    publishers = json.load(f)

print(f"Total publishers to upsert: {len(publishers)}")

# Normalize: every record must have ALL_KEYS
normalized = []
for r in publishers:
    rec = {}
    for k in ALL_KEYS:
        v = r.get(k)
        if v is None or str(v) == "nan":
            rec[k] = None
        else:
            rec[k] = v
    if rec["publisher_name"]:
        normalized.append(rec)

print(f"Normalized: {len(normalized)} records")

headers = {
    "apikey": ANON_KEY,
    "Authorization": f"Bearer {ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

ctx = ssl.create_default_context()

batch_size = 200
success = 0
errors = 0
error_details = []

for i in range(0, len(normalized), batch_size):
    batch = normalized[i:i+batch_size]
    batch_num = i // batch_size + 1
    total_batches = (len(normalized) + batch_size - 1) // batch_size

    data = json.dumps(batch).encode("utf-8")
    url = f"{SUPABASE_URL}/rest/v1/publishers"

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        resp = urllib.request.urlopen(req, context=ctx)
        success += len(batch)
        print(f"  Batch {batch_num}/{total_batches}: OK ({success} total)")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        errors += len(batch)
        print(f"  Batch {batch_num}/{total_batches}: ERROR {e.code}")

        # For duplicates, retry one-by-one with merge
        if "duplicate" in body.lower() or e.code == 409:
            recovered = 0
            for rec in batch:
                try:
                    single_data = json.dumps([rec]).encode("utf-8")
                    single_req = urllib.request.Request(url, data=single_data, headers=headers, method="POST")
                    urllib.request.urlopen(single_req, context=ctx)
                    recovered += 1
                except urllib.error.HTTPError:
                    pass
            success += recovered
            errors -= recovered
            print(f"    Recovered {recovered}/{len(batch)} via single insert")
        else:
            error_details.append(body[:200])

    if batch_num % 5 == 0:
        time.sleep(0.3)

print(f"\n=== IMPORT COMPLETE ===")
print(f"Success: {success}")
print(f"Errors: {errors}")
if error_details:
    print(f"Error samples: {error_details[:3]}")
