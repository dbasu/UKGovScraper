import requests
import os
from bs4 import BeautifulSoup
import json
import logging
from URLCreator import URLCreator
from http import cookiejar
from typing import Dict, Union
import time

class RejectAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

class UKGovScraper:
    def __init__(self,  dir: Union[str, None]) -> None:
        #create logger
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        #set up directory
        if dir is None:
            self.dir = os.path.join(os.getcwd() + '/data/')
        else:
            self.dir = dir
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        #set up search
        self.u = URLCreator(search=None)
        self.headers = {'User-agent': 'Mozilla/5.0'}
        #set up Session
        self.s = requests.Session()
        self.s.headers.update(self.headers)
        self.s.cookies.set_policy(RejectAll())
        #set up output
        self.links = []
        self.timeout = 30
        self.idle_time = 300
        self.max_page = None
        self.url = None

    def save_page(self, page: int, content)-> None:
        self.filename = os.path.join(self.dir, 'page' + str(page) + '.html')
        with open(self.filename, "wb") as f:
            f.write(content)
            self.logger.info("Page " + str(page) + " saved.")

    def get_page(self, url:str, page:int) -> BeautifulSoup:
        r = self.s.get(url, headers=self.headers, timeout=self.timeout) 
        if r.status_code == 200:
            self.save_page(page=page, content=r.content)
            return BeautifulSoup(r.text, features='html.parser')
        else:
            logging.error("Error: " + str(r.status_code))
            return None

    def scrape(self, search: Dict) -> str:
        self.u.set_search_parameters(search=search)
        self.u.create_url()
        self.url = self.u.target_url
        soup = self.get_page(url=self.url, page=1)

        if soup is not None:
            #get max page
            paginations = soup.find_all("a", {'class':['govuk-link', 'govuk-pagination__link']})
            for p in paginations:
                if p.get('rel', 'None') != ['next']:
                    next
                else:
                    self.max_page = int(p.get("data-ga4-link").split()[-1])
                    self.u.set_max_page(max_page=self.max_page)
                    self.logger.info("Max pages: " + str(self.max_page))
                    break
            self.links = self.get_links(soup)

        if self.max_page is not None:
            #sleep
            self.logger.info("Max pages: 1")
            time.sleep(self.idle_time)
            #loop through pages
            for page in range(2, self.max_page):
                self.url = self.u.next_page()
                soup = self.get_page(url=self.url, page=page)
                if soup is not None:
                    self.links.extend(self.get_links(soup))

                # sleep
                time.sleep(self.idle_time)
        return (self.links)


    def get_links(self, soup: BeautifulSoup) -> list:
        result = []
        for row in soup.find_all('li', class_='gem-c-document-list__item'):

            published_date = None
            title = None
            description = None
            link = None

            a = row.find_all('a', class_ ="govuk-link")
            p = row.find_all('p')
            ul = row.find_all('ul', class_="gem-c-document-list__item-metadata")
            if ul is not None:
                if len(ul) > 0:
                    li = ul[0].find_all('li', class_="gem-c-document-list__attribute")
                else:
                    li = None

            if li is not None:
                time_element = None
                if len(li) > 0:
                    time_element = li[0].find('time')
                if time_element is not None:
                    published_date = time_element.get('datetime')
                    self.logger.info(published_date)
                        
            if p is not None:
                if len(p) > 0:
                    description = p[0].text.strip()
                    self.logger.info(description)
            if a is not None:
                if len(a) > 0:
                    title = a[0].text.strip()
                    self.logger.info(title)
                    if 'href' in a[0].attrs:
                        if a[0]['href'].startswith('/'):
                            link = 'https://www.gov.uk' + a[0].get('href', None)
                        else:
                            link = a[0].get('href', None)
                        self.logger.info(link)
            result.append([published_date, title, description, link])

        return result