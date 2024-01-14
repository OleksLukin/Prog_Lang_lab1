import requests
from bs4 import BeautifulSoup
import time
from threading import Thread
from queue import Queue


class NewsExtractor:
    def __init__(self, url, extract_function):
        self.url = url
        self.extract_function = extract_function

    def extract_news(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error during request to {self.url}: {e}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        try:
            return self.extract_function(soup)
        except Exception as e:
            print(f"Error during parsing HTML from {self.url}: {e}")
            return None


class NewsUpdater:
    def __init__(self, url_extractors, update_time=30):
        self.url_extractors = url_extractors
        self.update_time = update_time
        self.news_queue = Queue()

    def update_news(self):
        while True:
            for url_extractor in self.url_extractors:
                news_data = url_extractor.extract_news()

                if news_data is not None and news_data not in self.news_queue.queue:
                    self.news_queue.put(news_data)

            time.sleep(self.update_time)

    def run(self):
        update_thread = Thread(target=self.update_news)
        update_thread.start()

        try:
            while True:
                if not self.news_queue.empty():
                    news_data = self.news_queue.get()
                    print(f"Title: {news_data['title']}")
                    print(f"Summary: {news_data['summary']}")
                    print(f"Author: {news_data['author']}")
                    print("-" * 50)
        except KeyboardInterrupt:
            print("Exiting...")
            update_thread.join()


def extract_news_site1(soup):
    title = soup.find("h3", class_="content-card__title").text.strip()
    summary = soup.find("div", class_="content-card__excerpt").text.strip()
    author = soup.find("div", class_="content-card__author").text.strip()
    return {"title": title, "summary": summary, "author": author}


def extract_news_site2(soup):
    title = soup.find("h2", class_="post-card__title").find("a").text.strip()
    summary = soup.find("div", class_="post-card__excerpt").text.strip()
    author = soup.find("div", class_="post-card__byline").find("a").text.strip()
    return {"title": title, "summary": summary, "author": author}


def extract_news_site3(soup):
    title = soup.find("h3", class_="entry-title").find("a").text.strip()
    summary = soup.find(
        "div", class_="newspack-post-subtitle--in-homepage-block"
    ).text.strip()
    author = soup.find("span", class_="author vcard").find("a").text.strip()
    return {"title": title, "summary": summary, "author": author}


if __name__ == "__main__":
    news_urls = [
        "https://theintercept.com/",
        "https://observer.com/",
        "https://chicagoreader.com/",
    ]

    url_extractors = [
        NewsExtractor(news_urls[0], extract_news_site1),
        NewsExtractor(news_urls[1], extract_news_site2),
        NewsExtractor(news_urls[2], extract_news_site3),
    ]

    updater = NewsUpdater(url_extractors)
    updater.run()
