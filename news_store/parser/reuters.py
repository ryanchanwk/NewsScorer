import datetime
import logging

import cfscrape
import pytz
import re
from bs4 import BeautifulSoup

from .base import BaseParser

logger = logging.getLogger(__name__)


class ReutersParser(BaseParser):

    @staticmethod
    def request_method(url):
        scraper = cfscrape.create_scraper()
        response = scraper.get(url)
        return response

    def parser(self, soup: BeautifulSoup):
        result = soup.find_all("div", class_='column1')[0]
        contents = result.find_all("article", {'class': 'story'})
        return_dict = {}

        for content in contents:
            if content.find_all("span", {'class': 'timestamp'}):
                raw_time = content.find_all("span", {'class': 'timestamp'})[0].text
                if not re.match('[0-9]{0,2}:[0-9]{0,2}\w\w EDT', raw_time):
                    continue
                else:
                    time = raw_time
            title = content.find_all("h3", {'class': 'story-title'})[0].text.replace('\t', '').replace('\n', '')
            body = content.find_all("p")[0].text.replace('\t', '').replace('\n\n', '').replace('\n', ' ').strip()
            raw_url = content.find_all('a')[0].attrs['href']
            url = f'https://www.reuters.com{raw_url}'
            return_dict[url] = {'title': title, 'body': body, 'time': time}
        return return_dict

    def post_process(self, result_dict):
        timezone_str = self.news_source.source_timezone

        try:
            source_timezone = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError as e:
            raise e

        for _, data in result_dict.items():
            for k in list(data.keys()):
                if k == 'time':
                    today_date = datetime.datetime.now(source_timezone)
                    today_date_str = datetime.datetime.strftime(today_date, '%Y-%m-%d')
                    datetime_str = f"{today_date_str} {data[k].upper().replace('EDT','')}"
                    data['datetime'] = source_timezone.localize(datetime.datetime.strptime(datetime_str.strip(),
                                                                                           '%Y-%m-%d %I:%M%p'))
        return result_dict

    def run(self) -> dict:
        url_list = [f'{self.news_source.source_url}&page={page}&pageSize=10' for page in range(1, 6)]
        all_result_dict = {}
        for url in url_list:
            soup = self.request(url)
            result_dict = self.parser(soup)
            result_dict = self.post_process(result_dict)
            all_result_dict.update(result_dict)
        return all_result_dict
