import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

with open("orgs.json", "r") as f:
    orgs = json.load(f)

with open("topics.json", "r") as f:
    topic_keywords = json.load(f)

results = []

for org in orgs:
    try:
        print(f"Scraping {org['name']}")
        response = requests.get(org["events_url"], timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Example selector; update per site
        event_items = soup.select("div.event, article, li.event")[:10]  # limit to top 10 events

        for event in event_items:
            title = event.get_text().strip()
            link = event.find("a")["href"] if event.find("a") else org["events_url"]

            matched_topics = []
            for topic, keywords in topic_keywords.items():
                if any(k.lower() in title.lower() for k in keywords):
                    matched_topics.append(topic)

            results.append({
                "Organization": org["name"],
                "Event Title": title,
                "Topics": ", ".join(matched_topics) if matched_topics else "Uncategorized",
                "Link": link
            })

    except Exception as e:
        print(f"Error scraping {org['name']}: {e}")

df = pd.DataFrame(results)
df.to_csv("output/tecna_event_topic_map.csv", index=False)
print("Done! File saved to output/tecna_event_topic_map.csv")
