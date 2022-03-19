import cfscrape
from bs4 import BeautifulSoup
import re
import datetime
import pytz
from .base import BaseParser


class FinvizParser(BaseParser):

    @staticmethod
    def request_method(url):
        scraper = cfscrape.create_scraper()
        response = scraper.get(url)
        return response

    def parser(self, soup: BeautifulSoup):
        result = soup.find_all("td", align="center", valign="top")
        content = result[2].find_all("tr")
        return_dict = {}
        for i in content:
            if i.find_all("td", class_="nn-date"):
                raw_time = i.find_all("td", class_="nn-date")[0].text
                if not re.match('\d\d:\d\d\w\w', raw_time):
                    continue
                else:
                    time = raw_time
            for j in i.find_all("td"):
                if j.get('data-boxover'):
                    text = j.get('data-boxover').replace('\t', '').replace('\n', '')
                    text = re.sub('cssbody=\[news_tooltip\-bdy\] cssheader=\[news_tooltip\-hdr\]', '', text)
                    text = re.sub('delay=\[\d+\]', '', text)
                    text = re.sub('<table width=\d+>', '', text)
                    text = re.sub('<tr>', '', text)
                    text = re.sub("<td class='news_tooltip-tab'>", '', text)
                    text = re.sub('</td>', '', text)
                    text = re.sub('</tr>', '', text)
                    text = re.sub('</table>', '', text)
                    text = re.sub(r'^https?:\/\/.[\r\n.]', '', text, flags=re.MULTILINE)
                    text = text.strip()
                    match_pat = re.match("body=\[([\w\W]+)\]", text)
                    text = match_pat.groups(0)[0]
                    content = text.strip()
            url = i.find("a").attrs['href']
            title = i.find("a").text
            return_dict[url] = {'title': title, 'body': content, 'time': time}
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
                    datetime_str = f'{today_date_str} {data[k]}'
                    data['datetime'] = source_timezone.localize(datetime.datetime.strptime(datetime_str,
                                                                                           '%Y-%m-%d %I:%M%p'))
        return result_dict
