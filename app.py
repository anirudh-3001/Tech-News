from flask import Flask, render_template, request
from news_fetcher import fetch_rss_tech, fetch_news_api_tech
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

# In-memory cache
CACHE = {"data": None, "timestamp": None}
CACHE_DURATION = timedelta(minutes=30)  # cache time

def get_cached_news():
    global CACHE
    now = datetime.utcnow()

    # ✅ Fixed: check properly if cache is valid
    if (
        CACHE["data"] is not None
        and isinstance(CACHE["data"], pd.DataFrame)
        and not CACHE["data"].empty
        and CACHE["timestamp"] is not None
        and now - CACHE["timestamp"] < CACHE_DURATION
    ):
        print("✅ Using cached news data.")
        return CACHE["data"]

    print("🔄 Fetching new data...")
    rss_df = fetch_rss_tech()
    api_df = fetch_news_api_tech()

    combined_df = pd.concat([rss_df, api_df], ignore_index=True)

    if not combined_df.empty:
        combined_df.drop_duplicates(subset="title", inplace=True)
        combined_df.sort_values(by="published", ascending=False, inplace=True)

    # Save to cache
    CACHE["data"] = combined_df
    CACHE["timestamp"] = now

    return combined_df

@app.route('/')
def home():
    selected_filter = request.args.get("filter", "All")
    combined_df = get_cached_news()

    if not combined_df.empty:
        if selected_filter != "All":
            combined_df = combined_df[
                combined_df["summary"].str.contains(selected_filter, case=False, na=False)
            ]
        news_items = combined_df.to_dict(orient="records")
    else:
        news_items = []

    return render_template('index.html', news=news_items, selected_filter=selected_filter)

if __name__ == '__main__':
    app.run(debug=True)
