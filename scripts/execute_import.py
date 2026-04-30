#!/usr/bin/env python3
"""Execute all upsert SQL batches against Supabase using REST API."""

import json
import os
import urllib.request
import ssl
import time

SUPABASE_URL = "https://izeixnkpquztaczehhum.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6ZWl4bmtwcXV6dGFjemVoaHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE2OTc3NzYsImV4cCI6MjA4NzI3Mzc3Nn0.Z2gk7lLoE3zQJQr2W4Em0A5w68r0JeqDBMcJJEW3A-U"

# Load master data
with open("/Volumes/workssd/ObsidianVault/scripts/output/publishers_master.json") as f:
    publishers = json.load(f)

print(f"Total publishers to upsert: {len(publishers)}")

# Use Supabase REST API for upsert (much faster than SQL)
# POST to /rest/v1/publishers with Prefer: resolution=merge-duplicates
# But we need the unique column to match on publisher_name

# Since we have a unique index on LOWER(publisher_name),
# we'll use the RPC approach or batch REST inserts

# Actually, the simplest: use postgREST upsert
# Headers needed
headers = {
    "apikey": ANON_KEY,
    "Authorization": f"Bearer {ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

ctx = ssl.create_default_context()

batch_size = 100
success = 0
errors = 0

for i in range(0, len(publishers), batch_size):
    batch = publishers[i:i+batch_size]
    batch_num = i // batch_size + 1
    total_batches = (len(publishers) + batch_size - 1) // batch_size

    # Clean up data for REST API
    clean_batch = []
    for r in batch:
        rec = {}
        for k, v in r.items():
            if v is not None and str(v) != "nan":
                rec[k] = v
        if "publisher_name" in rec:
            clean_batch.append(rec)

    if not clean_batch:
        continue

    data = json.dumps(clean_batch).encode("utf-8")
    url = f"{SUPABASE_URL}/rest/v1/publishers"

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        resp = urllib.request.urlopen(req, context=ctx)
        status = resp.getcode()
        success += len(clean_batch)
        if batch_num % 10 == 0 or batch_num == total_batches:
            print(f"  Batch {batch_num}/{total_batches}: {status} OK ({success} total)")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        errors += len(clean_batch)
        print(f"  Batch {batch_num}/{total_batches}: ERROR {e.code} - {body[:200]}")
        # If it's a conflict, try one-by-one
        if e.code == 409 or "duplicate" in body.lower():
            for rec in clean_batch:
                try:
                    single_data = json.dumps([rec]).encode("utf-8")
                    single_req = urllib.request.Request(url, data=single_data, headers=headers, method="POST")
                    urllib.request.urlopen(single_req, context=ctx)
                    success += 1
                    errors -= 1
                except:
                    pass

    # Small delay to avoid rate limiting
    if batch_num % 20 == 0:
        time.sleep(0.5)

print(f"\n=== IMPORT COMPLETE ===")
print(f"Success: {success}")
print(f"Errors: {errors}")
