import abc
import requests
from bs4 import BeautifulSoup


class AbstractParser(abc.ABC):

    @abc.abstractmethod
    def request(self):
        pass

    @abc.abstractmethod
    def parser(self):
        pass

    @abc.abstractmethod
    def post_process(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass


class BaseParser(AbstractParser):
    def __init__(self, news_source):
        self.news_source = news_source

    @staticmethod
    def request_method(url):
        return requests.get(url)

    def request(self, url):
        try:
            response = self.request_method(url)
            page = response.content
            soup = BeautifulSoup(page, 'lxml')
        except Exception as e:
            raise e
        return soup

    def parser(self, soup):
        return_dict = {}
        return return_dict

    def post_process(self, result_dict):
        return result_dict

    def run(self) -> dict:
        url = self.news_source.source_url
        soup = self.request(url)
        result_dict = self.parser(soup)
        result_dict = self.post_process(result_dict)
        return result_dict
