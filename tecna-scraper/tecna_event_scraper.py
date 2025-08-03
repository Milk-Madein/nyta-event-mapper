import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os

with open("orgs.json") as f:
    orgs = json.load(f)
with open("topics.json") as f:
    topic_map = json.load(f)

events = []

# Filter invalid titles
def is_valid_event_title(title):
    invalid_phrases = [
        "no events", "search", "category", "there are no", "upcoming events",
        "filter", "calendar", "archives"
    ]
    title = title.lower()
    return all(phrase not in title for phrase in invalid_phrases) and len(title.strip()) > 5

# Separate title/date
def split_title_and_date(text):
    if " – " in text:
        parts = text.split(" – ", 1)
    elif " - " in text:
        parts = text.split(" - ", 1)
    else:
        parts = [text, ""]
    return parts[0].strip(), parts[1].strip()

# Classify event type
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

# Classify topics
def classify_topics(text):
    text = text.lower()
    matched = [topic for topic, keywords in topic_map.items() if any(k.lower() in text for k in keywords)]
    return ", ".join(matched) if matched else "Uncategorized"

for org in orgs:
    try:
        res = requests.get(org["events_url"], timeout=10)
        if res.status_code != 200:
            continue
        soup = BeautifulSoup(res.text, "html.parser")

        # Example: Luma
        if "lu.ma" in org["events_url"]:
            for event in soup.select("a[href*='/event/']"):
                title = event.get_text(strip=True)
                link = event.get("href")
                if is_valid_event_title(title):
                    t, d = split_title_and_date(title)
                    events.append({
                        "organization": org["name"],
                        "event_title": t,
                        "event_date": d,
                        "event_type": classify_event_type(title),
                        "topics": classify_topics(title),
                        "link": link if link.startswith("http") else "https://lu.ma" + link
                    })

        # TechSTL structure
        elif "techstl.com" in org["events_url"]:
            for div in soup.select("div.wp-block-group"):
                title = div.get_text(strip=True)
                link = org["events_url"]
                if is_valid_event_title(title):
                    t, d = split_title_and_date(title)
                    events.append({
                        "organization": org["name"],
                        "event_title": t,
                        "event_date": d,
                        "event_type": classify_event_type(title),
                        "topics": classify_topics(title),
                        "link": link
                    })

        # Generic fallback
        else:
            for item in soup.select(".event, .tribe-event, li.event, article"):
                title = item.get_text(strip=True)
                link_tag = item.find("a")
                link = link_tag.get("href") if link_tag else org["events_url"]
                if is_valid_event_title(title):
                    t, d = split_title_and_date(title)
                    events.append({
                        "organization": org["name"],
                        "event_title": t,
                        "event_date": d,
                        "event_type": classify_event_type(title),
                        "topics": classify_topics(title),
                        "link": link
                    })

    except Exception as e:
        print(f"Failed for {org['name']}: {e}")

# DataFrame and export
df = pd.DataFrame(events)
df.columns = [col.strip() for col in df.columns]
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].astype(str).str.strip()

os.makedirs("output", exist_ok=True)
df.to_csv("output/tecna_event_topic_map.csv", index=False)
print("Saved: output/tecna_event_topic_map.csv")
