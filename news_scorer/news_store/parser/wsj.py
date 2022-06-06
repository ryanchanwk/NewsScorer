import datetime
import logging

import cfscrape
import pytz
import re
from bs4 import BeautifulSoup

from .base import BaseParser

logger = logging.getLogger(__name__)


class WSJParser(BaseParser):

    @staticmethod
    def request_method(url):
        scraper = cfscrape.create_scraper()
        response = scraper.get(url)
        return response

    def parser(self, soup: BeautifulSoup):
        return_dict = {}
        contents = soup.find_all("article", {'class': re.compile('WSJTheme--story')})
        for content in contents:
            try:
                title = content.find_all("span", {'class': re.compile('WSJTheme--headlineText*')})
                title = title[0].text.replace('\t', '').replace('\n', '')
                body = ''
                url = content.find_all('a')[0].attrs['href']
                article_tag = content.find_all("div", {'class': re.compile('WSJTheme--articleType*')})
                if article_tag:
                    article_tag = article_tag[0].text.replace('\t', '').replace('\n', '')
                else:
                    article_tag = None
                return_dict[url] = {'title': title, 'body': body, 'time': None, 'article_tag': article_tag}
            except:
                logger.error(f'Parser error in {content.text}')
                continue
        return return_dict

    def detail_parser(self, return_dict):
        for url in return_dict.keys():
            try:
                scraper = cfscrape.create_scraper()
                page = scraper.get(url).content
                soup = BeautifulSoup(page, 'lxml')

                if soup.find_all("time", {'class': re.compile('timestamp article__timestamp*')}):
                    return_dict[url]['time'] = \
                        soup.find_all("time", {'class': re.compile('timestamp article__timestamp*')})[0].text
                else:
                    logger.warning(f'{url} do not have dt info')
                    continue

                raw_sub_head = soup.find_all("h2", {'class': 'sub-head'})
                if len(raw_sub_head) > 0:
                    sub_head = raw_sub_head[0].text.replace('\t', '').replace('\n\n', '').replace('\n', ' ').strip()
                    sub_head = f'{sub_head}.'
                else:
                    sub_head = ''

                raw_body = soup.find_all("div", {'class': 'wsj-snippet-body'})
                if len(raw_body) > 0:
                    body = raw_body[0].text.replace('\t', '').replace('\n\n', '').replace('\n', ' ').strip()
                else:
                    body = ''
                return_dict[url]['body'] = f'{sub_head} {body}'
                logger.info(f'Body parser {url} finish.')
            except:
                logger.error(f'Body parser error in {url}')
                continue
        return return_dict

    def post_process(self, result_dict):
        month_map = {'Jan.': 'Jan', 'Feb.': 'Feb', 'March': 'Mar',  'April': 'Apr',
                     'May': 'May', 'Jun.': 'Jun', 'June': 'Jun', 'July': 'Jul', 'Aug.': 'Aug',
                     'Sept.': 'Sep', 'Oct.': 'Oct', 'Nov.': 'Nov', 'Dec.': 'Dec'}
        timezone_str = self.news_source.source_timezone

        try:
            source_timezone = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError as e:
            raise e

        processed_dict = {}

        for url, data in result_dict.items():
            if data.get('time'):
                if data['time'] is not None:
                    raw_datetime = data['time']
                    for month_key in month_map.keys():
                        raw_datetime = raw_datetime.replace(month_key, month_map[month_key])
                    datetime_str = f"{raw_datetime.replace('ET', '').replace('Updated', '').replace('Published', '').strip()}"
                    try:
                        data['datetime'] = source_timezone.localize(datetime.datetime.strptime(datetime_str.strip(),
                                                                                               '%b %d, %Y %I:%M %p'))
                    except ValueError:  # some news don't have time
                        data['datetime'] = source_timezone.localize(datetime.datetime.strptime(datetime_str.strip(),
                                                                                               '%b %d, %Y'))
                    processed_dict[url] = data

        return processed_dict

    def run(self) -> dict:
        url = self.news_source.source_url
        soup = self.request(url)
        result_dict = self.parser(soup)
        result_dict = self.detail_parser(result_dict)
        result_dict = self.post_process(result_dict)
        return result_dict
