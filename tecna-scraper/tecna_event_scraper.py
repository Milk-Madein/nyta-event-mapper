import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os
import re

with open("orgs.json") as f:
    orgs = json.load(f)
with open("topics.json") as f:
    topic_map = json.load(f)

# Normalize location
def normalize_location(raw_location):
    if not raw_location:
        return "Unknown"

    text = raw_location.strip().lower()

    if any(term in text for term in ["virtual", "online", "remote"]):
        return "Virtual"
    if any(term in text for term in ["tbd", "n/a", "not available", "unknown"]):
        return "Unknown"

    text = re.sub(r"[\s,]+", " ", text).title().strip()

    replacements = {
        "Washington D.C.": "Washington, DC",
        "Washington Dc": "Washington, DC",
        "Ny": "NY",
        "Tx": "TX",
        "Ca": "CA",
        "Dc": "DC"
    }

    for wrong, right in replacements.items():
        text = re.sub(rf"\b{wrong}\b", right, text, flags=re.IGNORECASE)

    return text

def is_valid_event_title(title):
    invalid_phrases = [
        "no events", "search", "category", "there are no", "upcoming events",
        "filter", "calendar", "archives"
    ]
    title = title.lower()
    return all(phrase not in title for phrase in invalid_phrases) and len(title.strip()) > 5

def split_title_and_date_regex(text):
    date_pattern = r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-.,]*\d{1,2}[a-z]*[\s,]*\d{4})"
    match = re.search(date_pattern, text, re.IGNORECASE)
    if match:
        date_str = match.group(0).strip()
        title_clean = text.replace(date_str, "").strip(" -–,")
        return title_clean, date_str
    return text.strip(), ""

def classify_event_type(text):
    text = text.lower()
    if "virtual" in text:
        return "Virtual"
    elif "webinar" in text:
        return "Webinar"
    elif "in-person" in text or "onsite" in text:
        return "In-Person"
    elif "hybrid" in text:
        return "Hybrid"
    else:
        return "Uncategorized"

def classify_topics(text):
    text = text.lower()
    matched = [topic for topic, keywords in topic_map.items() if any(k.lower() in text for k in keywords)]
    return ", ".join(matched) if matched else "Uncategorized"

events = []

for org in orgs:
    try:
        res = requests.get(org["events_url"], timeout=10)
        if res.status_code != 200:
            continue
        soup = BeautifulSoup(res.text, "html.parser")

        if "lu.ma" in org["events_url"]:
            for event in soup.select("a[href*='/event/']"):
                title = event.get_text(strip=True)
                link = event.get("href")
                location = event.get("data-location", "")
                description = event.get("title", "")
                if is_valid_event_title(title):
                    t, d = split_title_and_date_regex(title)
                    events.append({
                        "organization": org["name"],
                        "event_title": t,
                        "event_date": d,
                        "event_type": classify_event_type(title),
                        "topics": classify_topics(title),
                        "location": normalize_location(location),
                        "description": description,
                        "link": link if link.startswith("http") else "https://lu.ma" + link
                    })

        elif "techstl.com" in org["events_url"]:
            for div in soup.select("div.wp-block-group"):
                title = div.get_text(strip=True)
                description = div.find_next("p").get_text(strip=True) if div.find_next("p") else ""
                link = org["events_url"]
                if is_valid_event_title(title):
                    t, d = split_title_and_date_regex(title)
                    events.append({
                        "organization": org["name"],
                        "event_title": t,
                        "event_date": d,
                        "event_type": classify_event_type(title),
                        "topics": classify_topics(title),
                        "location": "Unspecified",
                        "description": description,
                        "link": link
                    })

        else:
            for item in soup.select(".event, .tribe-event, li.event, article"):
                title = item.get_text(strip=True)
                link_tag = item.find("a")
                link = link_tag.get("href") if link_tag else org["events_url"]
                location = ""
                description = ""
                if item.find("time"):
                    description = item.find("time").get("datetime", "")
                if is_valid_event_title(title):
                    t, d = split_title_and_date_regex(title)
                    events.append({
                        "organization": org["name"],
                        "event_title": t,
                        "event_date": d,
                        "event_type": classify_event_type(title),
                        "topics": classify_topics(title),
                        "location": normalize_location(location),
                        "description": description,
                        "link": link
                    })

    except Exception as e:
        print(f"Failed for {org['name']}: {e}")

df = pd.DataFrame(events)
df.columns = [col.strip() for col in df.columns]
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].astype(str).str.strip()

os.makedirs("output", exist_ok=True)
df.to_csv("output/tecna_event_topic_map.csv", index=False)
print("Saved: output/tecna_event_topic_map.csv")
