import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import aiohttp

import requests
import logging
from newsapi import NewsApiClient

load_dotenv()

news_api_key = os.getenv('news_api_key')
reddit_token = os.getenv('reddit_token')
reddit_user_agent = os.getenv('reddit_user_agent')

# to get the auth reddit_personal_script_key and secret_reddit_personal_script_token
# head to https://www.reddit.com/prefs/apps -> search page for "developed application" -> click edit and copy
# the values
reddit_personal_script_key = os.getenv('reddit_personal_script_key')
secret_reddit_personal_script_token = os.getenv('secret_reddit_personal_script_token')


class NewsAdapter(ABC):
    def __init__(self):
        self.async_supported = False
        self.setup()

    @abstractmethod
    def setup(self):
        """
        setup the data needed for activating the integration of the provider api.
        :return: None
        """
        pass

    @abstractmethod
    def check_news_exist(self, news_data: dict):
        """
        checks if the news exist from the api response or if it is empty.
        :param news_data: the news data that's returned from the news api.
        :return: the status of the news if they exist or not.
        """
        pass

    @abstractmethod
    def list_news(self, page_size, category) -> list:
        """
        lists the top news data that the api provider provides.
        :param page_size: the number of news that to be returned.
        :param category: the category of the news that the search should include.
        :return: a list of news that's formatted in a unified way as following:
            [
              {
                "headline": "",  // Headline of the article
                "link": "",  // Link of the article
                "source": "" // Source that you retrieved this news from
              },
            ]
        """
        pass

    @abstractmethod
    def extract_news(self, news_data: dict) -> dict:
        """
        converts the news from their original api data a generalized structure for the results api.
        :param news_data: the data that's returned from the news api.
        :return: the data that's ready to be served as a result.
        """
        pass

    @abstractmethod
    def search_news(self, keyword, page_size, category, sort_by) -> list:
        """
        searches through the news and return the news that matches certain keyword.
        :param keyword: the search keyword to get the search results.
        :param page_size: the length of the news results.
        :param category: the news category the search will include.
        :param sort_by: the way the results are sorted
        :return: the list of news as a result.
        """
        pass


class NewsAPINews(NewsAdapter):

    def setup(self):
        """
        setup the data needed for activating the integration with the news api api.
        references:
            https://newsapi.org/docs/client-libraries/python
            https://newsapi.org/docs/authentication
        :return: None
        """
        self.news_api = NewsApiClient(api_key=news_api_key)

    def list_news(self, page_size=2, category="general") -> list:
        """
        lists the breaking news from the "newsapi" api.

        :param page_size: the number of news that to be returned.
        :param category: the category of the news that the search is looking for, the options are:
            - business
            - entertainment
            - general
            - health
            - science
            - sports
            - technology
        :return: a list of news that's formatted in the  parent class structure.
        """
        news_data = self.news_api.get_top_headlines(
            category=category, language='en', page_size=page_size
        )
        news_response = self.extract_news(news_data)
        return news_response

    def check_news_exist(self, news_data: dict) -> bool:
        """
        checks if the news exist from the "newsapi" api response or if it is empty.
        :param news_data: the news data that's returned from the news api.
        :return: the status of the news if they exist or not.
        """
        request_status = news_data.get("status", False)
        number_of_results = news_data.get("totalResults", 0)
        news_exist = request_status and number_of_results != 0
        return news_exist

    def extract_news(self, news_data: dict) -> list:
        """
        converts the news from their original api data a generalized structure for the results api.
        :param news_data: the data that's returned from the news api.
        :return: the data that's ready to be served as a result.
        """
        news_exist = self.check_news_exist(news_data=news_data)
        if not news_exist:
            return []

        articles = news_data.get("articles")
        news_response = [
            {
                "headline": article.get("title", ""),
                "link": article.get("url", ""),
                "source": "newsapi"
            }
            for article in articles
        ]

        return news_response

    def search_news(self, keyword, page_size=2, category="general", sort_by="relevancy"):
        """
        searches through the "newsapi" news and return the news that match certain keyword.
        reference: https://newsapi.org/docs/endpoints/everything
        :param keyword: the search keyword to get the search results.
        :param page_size: the length of the news results.
        :param category: the news category the search will include, the options are:
            - business
            - entertainment
            - general
            - health
            - science
            - sports
            - technology
        :param sort_by: the way the results are sorted, options are:
            relevancy = articles more closely related to q come first.
            popularity = articles from popular sources and publishers come first.
            publishedAt = newest articles come first.
        :return: the list of news as a result.
        """

        news_data = self.news_api.get_everything(q=keyword, language='en', page_size=page_size, sort_by=sort_by)
        news_response = self.extract_news(news_data)

        return news_response


class RedditAPINews(NewsAdapter):

    def setup(self):
        """
        setup the data needed for activating the integration with the reddit api.
        :return: None
        """
        self.headers = {'Authorization': f"bearer {reddit_token}", "User-Agent": reddit_user_agent}
        self.async_supported = True

    async def list_news(self, session: aiohttp.ClientSession, page_size=2, category="news") -> list:
        """
        lists the breaking news from the "newsapi" api.

        :param session: aiohttp session to support async operations.
        :param page_size: the number of news that to be returned.
        :param category: the subreddit that the search is looking in.
        :return: a list of news that's formatted in the parent class structure.
        """
        params = {"limit": page_size}
        response = await session.get(f"https://oauth.reddit.com/r/{category}/hot", params=params, headers=self.headers)

        if response.status != 200:
            logging.warning(
                f"the reddit news api in `RedditAPINews.list_news` returned unexpected status: {response.status}"
            )
            return []

        news_data = await response.json()
        news_response = self.extract_news(news_data)
        return news_response

    def check_news_exist(self, news_data: dict) -> bool:
        """
        checks if the news exist from the "newsapi" api response or if it is empty.
        :param news_data: the news data that's returned from the news api.
        :return: the status of the news if they exist or not.
        """

        news_exist = news_data.get("data", {}).get("dist", 0) != 0

        return news_exist

    def extract_news(self, news_data: dict) -> list:
        """
        converts the news from their original api data a generalized structure for the results api.
        :param news_data: the data that's returned from the news api.
        :return: the data that's ready to be served as a result.
        """
        news_exist = self.check_news_exist(news_data=news_data)
        if not news_exist:
            return []

        news_list = news_data.get("data")['children']

        news_response = [
            {
                "headline": news.get("data", {}).get("title", ""),
                "link": news.get("data", {}).get("url", ""),
                "source": "reddit"
            }
            for news in news_list
        ]

        return news_response

    async def search_news(
            self, keyword, session: aiohttp.ClientSession, page_size=2, category="general", sort_by="relevancy"
    ):
        """
        searches through the "newsapi" news and return the news that match certain keyword.
        reference: https://newsapi.org/docs/endpoints/everything
        :param session:
        :param keyword: the search keyword to get the search results.
        :param page_size: the length of the news results.
        :param category: the news category the search will include, the options are:
            - business
            - entertainment
            - general
            - health
            - science
            - sports
            - technology
        :param sort_by: the way the results are sorted, options are:
            relevancy = articles more closely related to q come first.
            popularity = articles from popular sources and publishers come first.
            publishedAt = newest articles come first.
        :return: the list of news as a result.
        """
        params = {
            "limit": 2,
            "q": keyword
        }
        response = await session.get("https://oauth.reddit.com/r/news/search", params=params, headers=self.headers)

        if response.status != 200:
            logging.warning(
                f"the reddit news api in `RedditAPINews.search_news` returned unexpected status: {response.status}"
                f" with keyword: {keyword}"
            )
            return []

        news_data = await response.json()

        news_response = self.extract_news(news_data)

        return news_response

    @staticmethod
    def generate_reddit_token(username, password, user_agent=reddit_user_agent):
        """
        generate the reddit token so you can use it to the reddit api.
        :param username: the reddit username.
        :param password: the reddit password.
        :param user_agent: the reddit bot name.
        :return: the reddit token to access the reddit APIs that's protected by authentication.
        """
        data = {'grant_type': 'password', 'username': username, 'password': password}
        auth = requests.auth.HTTPBasicAuth(reddit_personal_script_key, secret_reddit_personal_script_token)
        headers = {'User-Agent': user_agent}
        res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
        new_reddit_token = res.json()['access_token']
        return new_reddit_token
