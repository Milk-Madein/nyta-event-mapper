import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os

# Load org and topic data
with open("orgs.json") as f:
    orgs = json.load(f)
with open("topics.json") as f:
    topic_map = json.load(f)

events = []

# Basic scraper logic (placeholder for real scraping)
for org in orgs:
    try:
        res = requests.get(org['events_url'], timeout=10)
        if res.status_code != 200:
            continue
        soup = BeautifulSoup(res.text, 'html.parser')
        # Placeholder: simulate event title for demonstration
        events.append({
            "organization": org["name"],
            "event_title": "Sample Event Title",
            "link": org["events_url"]
        })
    except Exception as e:
        print(f"Failed for {org['name']}: {e}")

# Convert to DataFrame
df = pd.DataFrame(events)

# Clean data
df.columns = [col.strip() for col in df.columns]
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].astype(str).str.strip()

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Save cleaned CSV
df.to_csv("output/tecna_event_topic_map.csv", index=False)
