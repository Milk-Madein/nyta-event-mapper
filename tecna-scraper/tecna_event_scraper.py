import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os

with open("orgs.json") as f:
    orgs = json.load(f)

events = []

# Helper to filter out non-event titles
def is_valid_event_title(title):
    invalid_phrases = [
        "no events", "search", "category", "there are no", "upcoming events",
        "filter", "calendar", "archives"
    ]
    title = title.lower()
    return all(phrase not in title for phrase in invalid_phrases) and len(title.strip()) > 5

for org in orgs:
    try:
        res = requests.get(org["events_url"], timeout=10)
        if res.status_code != 200:
            continue
        soup = BeautifulSoup(res.text, "html.parser")

        # Example 1: Luma-based events (e.g., TechBuffalo)
        if "lu.ma" in org["events_url"]:
            for event in soup.select("a[href*='/event/']"):
                title = event.get_text(strip=True)
                link = event.get("href")
                if is_valid_event_title(title):
                    events.append({
                        "organization": org["name"],
                        "event_title": title,
                        "link": link if link.startswith("http") else "https://lu.ma" + link
                    })

        # Example 2: TechSTL (uses div.wp-block-group)
        elif "techstl.com" in org["events_url"]:
            for div in soup.select("div.wp-block-group"):
                title = div.get_text(strip=True)
                link = org["events_url"]
                if is_valid_event_title(title):
                    events.append({
                        "organization": org["name"],
                        "event_title": title,
                        "link": link
                    })

        # Example 3: Generic structure
        else:
            for item in soup.select(".event, .tribe-event, li.event, article"):
                title = item.get_text(strip=True)
                link_tag = item.find("a")
                link = link_tag.get("href") if link_tag else org["events_url"]
                if is_valid_event_title(title):
                    events.append({
                        "organization": org["name"],
                        "event_title": title,
                        "link": link
                    })

    except Exception as e:
        print(f"Failed for {org['name']}: {e}")

# Clean and export
df = pd.DataFrame(events)
df.columns = [col.strip() for col in df.columns]
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].astype(str).str.strip()

os.makedirs("output", exist_ok=True)
df.to_csv("output/tecna_event_topic_map.csv", index=False)
print("Saved: output/tecna_event_topic_map.csv")
