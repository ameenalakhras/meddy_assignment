from fastapi import FastAPI
from utils import RedditAPINews, NewsAPINews
import asyncio
import aiohttp

reddit_api = RedditAPINews()
news_api = NewsAPINews()
supported_news_objects = [reddit_api, news_api]

app = FastAPI()


@app.get("/news")
async def list_news():
    results = []
    not_supported_async_objects = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for news_object in supported_news_objects:
            if news_object.async_supported:
                tasks.append(news_object.list_news(session))
            else:
                not_supported_async_objects.append(news_object)

        for news_object in not_supported_async_objects:
            results += news_object.list_news()
        results += await asyncio.gather(*tasks)

    return results


@app.get("/news?query={keyword}")
async def search_news(keyword: str):
    results = []
    not_supported_async_objects = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for news_object in supported_news_objects:
            if news_object.async_supported:
                tasks.append(news_object.search_news(session=session, keyword=keyword))
            else:
                not_supported_async_objects.append(news_object)

        for news_object in not_supported_async_objects:
            results += news_object.search_news(keyword=keyword)
        results += await asyncio.gather(*tasks)

    return results
