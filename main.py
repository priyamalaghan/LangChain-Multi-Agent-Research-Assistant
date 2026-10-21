from src.tools.tools import web_search, scrape_url

results = web_search.invoke({
    "query" : "Latest news on AI research"
    })
print(results)

results = scrape_url.invoke({
    "url" : "https://www.crescendo.ai/news/latest-ai-news-and-updates"
    })
print(results)