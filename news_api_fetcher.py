import requests
import pandas as pd
from datetime import datetime
import spacy
import re
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_sm")

NEWS_API_KEY = "7f2a7b9c915d4a8eb8f33bb8a184e417"

TECH_TERMS = [
    # AI & ML
    "AI research", "AI R&D", "artificial intelligence", "machine learning", "deep learning",
    "AI accelerator", "AI infrastructure", "AI chip", "AI startup", "AI breakthrough", "AI model",

    # Software & Developer Tools
    "software engineering", "developer tools", "cloud computing", "data science",
    "API platform", "SDK", "framework", "automation tools", "enterprise SaaS", "open-source",

    # Launches & Innovation
    "product launch", "software release", "platform launch", "innovation lab",
    "new feature", "beta release", "technical preview", "developer conference", "GPT update",

    # Investment & Funding
    "startup funding", "series A", "series B", "tech investment", "R&D investment",
    "venture capital", "strategic partnership", "research grant", "AI funding"
]

COMPANY_TERMS = [
    "OpenAI", "DeepMind", "Anthropic", "NVIDIA", "Microsoft", "Meta", "Amazon", "Google", "IBM",
    "Databricks", "Salesforce", "Oracle", "SAP", "Intel", "Qualcomm",
    "Adobe", "Snowflake", "Palantir", "UiPath", "ServiceNow", "Infosys",
    "Wipro", "Tata Consultancy Services", "Goldman Sachs", "JPMorgan Chase",
    "Morgan Stanley", "Cognizant", "Accenture", "Capgemini", "DXC Technology",
    "HCL Technologies", "LTI", "Tech Mahindra", "Virtusa", "Mphasis", "Zensar Technologies"
]

def clean_summary(text):
    return BeautifulSoup(text, "html.parser").get_text()

def is_relevant(text):
    # Keyword and company matching
    keyword_match = any(term.lower() in text for term in TECH_TERMS + COMPANY_TERMS)

    # Detect meaningful tech-related events
    phrase_match = bool(re.search(
        r"(launched|introduced|released|rolled out|announced|unveiled|raised|secured|funding|partnership|investment|AI model|update)",
        text
    ))

    # Named entity recognition: organizations or money involved
    doc = nlp(text)
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    money = [ent.text for ent in doc.ents if ent.label_ == "MONEY"]
    entity_boost = bool(orgs or money)

    # Prioritize relevance by combining signals
    return keyword_match or phrase_match or entity_boost


def fetch_news_api_tech():
    urls = [
        f"https://newsapi.org/v2/everything?q=(ChatGPT OR OpenAI OR tech+launch OR AI+update OR software+innovation OR India+AI OR developer+tools)&language=en&sortBy=publishedAt&pageSize=50&apiKey={NEWS_API_KEY}",
        f"https://newsapi.org/v2/top-headlines?category=technology&language=en&country=in&apiKey={NEWS_API_KEY}"
    ]

    all_articles = []
    for url in urls:
        try:
            response = requests.get(url)
            data = response.json()
            articles = data.get("articles", [])
        except Exception as e:
            print("Error fetching:", e)
            continue

        for a in articles:
            title = a.get("title", "")
            desc = clean_summary(a.get("description", "") or "")
            text = (title + " " + desc).lower()

            if is_relevant(text):
                all_articles.append({
                    "title": title,
                    "summary": desc,
                    "link": a.get("url"),
                    "published": a.get("publishedAt", datetime.utcnow().isoformat()),
                    "source": a.get("source", {}).get("name", "")
                })

    df = pd.DataFrame(all_articles)
    if not df.empty:
        df['published'] = pd.to_datetime(df['published'], errors='coerce').astype(str)
    return df
