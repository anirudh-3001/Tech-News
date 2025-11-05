import feedparser
import requests
import pandas as pd
from datetime import datetime
import re
import spacy

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

NEWS_API_KEY = "7f2a7b9c915d4a8eb8f33bb8a184e417"  # replace with your key

RSS_FEEDS = [
    # AI & Tech Industry
    "https://feeds.feedburner.com/TheHackersNews",
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/ai/index.xml",
    "https://venturebeat.com/feed/",
    "https://www.zdnet.com/news/rss.xml",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",

    # Developer & Software Engineering
    "https://dev.to/feed",
    "https://thenewstack.io/feed/",
    "https://www.infoq.com/feed/",
    "https://hackaday.com/blog/feed/",
    "https://opensource.com/feed",

    # AI Research & Innovation
    "https://www.analyticsvidhya.com/blog/feed/",
    "https://spectrum.ieee.org/feed",
    "https://research.google/blog/feed/",
    "https://openai.com/blog/rss/",
    "https://deepmind.google/rss.xml",
    "https://ai.googleblog.com/feeds/posts/default",

    # Indian & Global Tech Business
    "https://www.moneycontrol.com/rss/technology.xml",
    "https://gadgets360.com/rss/news",
    "https://www.livemint.com/rss/technology",
    "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    "https://indianexpress.com/section/technology/feed/",

    # Startups & Funding
    "https://yourstory.com/feed",
    "https://inc42.com/feed/",
    "https://tech.economictimes.indiatimes.com/rss/topstories",
]

def clean_summary(text):
    return re.sub(r'<.*?>', '', text or "").strip()

def generate_contextual_summary(title, description):
    text = f"{title}. {description}"
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    if len(sentences) >= 2:
        return " ".join(sentences[:2])
    return text.strip()

def is_relevant(text):
    keywords = [
        "ai", "artificial intelligence", "machine learning", "deep learning", "neural network",
        "chatgpt", "openai", "llm", "gemini", "claude", "copilot",
        "software", "update", "release", "version", "microsoft", "google", "aws", "cloud",
        "startup", "launch", "tech company", "product",
        "india", "indian", "bangalore", "bengaluru", "hyderabad"
    ]
    score = sum(1 for k in keywords if k in text)
    return score >= 2

def fetch_rss_tech():
    all_articles = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = clean_summary(entry.get("summary", ""))
            text = (title + " " + summary).lower()
            if is_relevant(text):
                contextual_summary = generate_contextual_summary(title, summary)
                all_articles.append({
                    "title": title,
                    "summary": contextual_summary,
                    "link": entry.get("link", ""),
                    "published": entry.get("published", datetime.utcnow().isoformat()),
                    "source": feed.feed.get("title", "RSS Feed")
                })
    return pd.DataFrame(all_articles)

def fetch_news_api_tech():
    urls = [
        f"https://newsapi.org/v2/everything?q=(AI OR artificial+intelligence OR ChatGPT OR OpenAI OR DeepMind OR startup+funding OR tech+innovation OR cloud+computing)&language=en&sortBy=publishedAt&pageSize=50&apiKey={NEWS_API_KEY}",
        f"https://newsapi.org/v2/top-headlines?category=technology&language=en&country=in&apiKey={NEWS_API_KEY}",
        f"https://newsapi.org/v2/everything?q=(software+update OR developer+tools OR data+science OR SaaS+platform)&language=en&sortBy=publishedAt&pageSize=50&apiKey={NEWS_API_KEY}",
         f"https://newsapi.org/v2/everything?q=(India+AI OR Indian+startup OR Bengaluru+AI OR Hyderabad+tech OR TCS+software OR Infosys+AI OR Wipro+cloud OR Tech+Mahindra)&language=en&sortBy=publishedAt&pageSize=50&apiKey={NEWS_API_KEY}",

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
                contextual_summary = generate_contextual_summary(title, desc)
                all_articles.append({
                    "title": title,
                    "summary": contextual_summary,
                    "link": a.get("url"),
                    "published": a.get("publishedAt", datetime.utcnow().isoformat()),
                    "source": a.get("source", {}).get("name", "")
                })

    df = pd.DataFrame(all_articles)
    if not df.empty:
        df['published'] = pd.to_datetime(df['published'], errors='coerce').astype(str)
    return df
