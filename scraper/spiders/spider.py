# -*- coding: utf-8 -*-

import re
import scrapy
import logging
from scraper.items import AppItem, AppItemLoader
from scraper.selector import Selector


class PlayStoreSpider(scrapy.Spider):
    name = 'playstorescrapy'
    allowed_domains = ["google.com"]
    start_urls = []

    CRAWL_URL = 'https://play.google.com/store/search?q={0}&c=apps'
    APP_URLS = "//a[@class='Si6A0c Gy4nib']/@href"

    # count how many items have been scraped
    item_count = 0

    def __init__(self, keywords=None, max_item=0, download_delay=0, output='item.csv',
                 email=None, password=None, *args, **kwargs):
        """
        :param keywords: search keywords separated by comma (required).
        :param max_item: maximum items to be scraped.
        :param download_delay: download delay (in seconds).
        :param output: output filename path.
        :param email: login email.
        :param password: login password.
        :param args: additional list of arguments.
        :param kwargs: additional dictionary of arguments.
        """

        super(PlayStoreSpider, self).__init__(*args, **kwargs)

        if keywords:
            arr_keywords = keywords.split(",")
            for keyword in arr_keywords:
                self.start_urls.append(self.CRAWL_URL.format(keyword.strip()))
        else:
            self.show_help()
            raise ValueError('"keywords" parameter is required')

        try:
            self.max_item = int(max_item)
        except ValueError:
            raise ValueError(
                '"max_item" parameter is invalid: ' + str(max_item))

        try:
            self.download_delay = int(download_delay)
        except ValueError:
            raise ValueError(
                '"download_delay" parameter is invalid: ' + str(download_delay))

        if output:
            self.output_file = output.strip()
        else:
            raise ValueError('"output" parameter is invalid: ' + str(output))

        if email:
            self.email = email.strip().lower()
            if password:
                self.password = password
            else:
                import getpass
                self.password = getpass.getpass('Please enter password: ')
        else:
            self.email = None
            self.password = None

    @staticmethod
    def show_help():
        print('show_help-----------------------------------------------------------')
        print(
            '\n>>> Command Usage: scrapy crawl playstorescrapy -a keywords=<comma_separated_keywords> [options]')
        print('>>> Options:')
        print('>>>  -a max_item=<number>          Specify maximum number of scraped items (default=0)')
        print('>>>  -a output=<filename>          Specify output filename path (default=item.csv)')
        print('>>>  -a download_delay=<number>    Specify download delay in seconds (default=0)')
        print('>>>  -a email=<email>              Specify login email')
        print('>>>  -a "password=<password>"      Specify login password (note: the double-quotes is required)')
        print('')

    # override
    def start_requests(self):
        print('start_requests-----------------------------------------------------------')
        """
        If email is provided, go to login process first.
        If email is not provided, directly launch the scraping requests.
        """

        if self.email:
            return self.open_google()
        else:
            return self.launch_requests()

    def open_google(self):
        print('open_google-----------------------------------------------------------')
        """
        Open google page to set up the cookie before login.
        """

        return [scrapy.Request('https://accounts.google.com/ServiceLogin?hl=en&continue=https://www.google.com/%3Fgws_rd%3Dssl',
                               callback=self.login)]

    def login(self, response):
        print('login-----------------------------------------------------------')
        """
        Login to google account.
        """

        galx = ''
        match = re.search(
            r'<input\s+name="GALX"[\s\S]+?value="(.+?)">', response.body, flags=re.M)
        if match:
            galx = match.group(1)
        return [
            scrapy.FormRequest("https://accounts.google.com/ServiceLoginAuth",
                               callback=self.after_login,
                               formdata={
                                   'Email': self.email,
                                   'Passwd': self.password,
                                   'PersistentCookie': 'yes',
                                   'GALX': galx,
                                   'continue': 'https://www.google.com/?gws_rd=ssl',
                                   'hl': 'en',
                               })
        ]

    def is_login_success(self, response):
        print('is_login_success-----------------------------------------------------------')
        """
        Check if login is success.
        :param response: Response object.
        :return: True if success else False.
        """

        email = re.escape(self.email)
        regex = r'<div\s+id="mngb">.+<span.+>' + email + r'\<'
        if re.search(regex, response.body):
            self.email = None
            self.password = None
            return True
        else:
            return False

    def after_login(self, response):
        print('after_login-----------------------------------------------------------')
        """
        Check if login success or not.
        If success, continue to scrape the pages.
        """

        if self.is_login_success(response):
            logging.info("**** Login success")
            self.email = None
            self.password = None
            return self.launch_requests()
        else:
            logging.warning("**** Login failed")
            return

    def launch_requests(self):
        print('launch_requests-----------------------------------------------------------')
        """
        Launch the scraping requests for each of keywords.
        """

        requests = []

        for url in self.start_urls:
            requests.append(scrapy.FormRequest(
                url,
                formdata={
                    'ipf': '1',
                    'xhr': '1',
                },
                callback=self.parse_search_page))

        return requests

    def parse_search_page(self, response):
        print(
            'parse_search_page-----------------------------------------------------------')
        """
        Parse search page.
        """

        if self.is_max_item_reached():
            logging.debug("**** Max Item reached")
            return

        logging.info("**** Scraping: " + response.url)

        app_urls = Selector(xpath=self.APP_URLS).get_value_list(response)
        if (app_urls != None):
            for url in app_urls:
                # parse app detail page
                yield scrapy.Request(AppItem.APP_URL_PREFIX + url + "&hl=pt-br", callback=self.parse_app_url)
            else:
                # parse next stream data if exist
                page_token = self.get_page_token(response.body)
                if page_token is not None:
                    yield scrapy.FormRequest(
                        response.url,
                        formdata={
                            'ipf': '1',
                            'xhr': '1',
                            'pagTok': page_token,
                        },
                        callback=self.parse_search_page)

    def is_max_item_reached(self):
        print(
            'is_max_item_reached-----------------------------------------------------------')
        """
        Check if max_item has been reached.
        :return: True if max_item has been reached else False.
        """

        return self.max_item > 0 and self.item_count >= self.max_item

    @staticmethod
    def get_page_token(content):
        print('get_page_token-----------------------------------------------------------')
        """
        Get "pagTok" value from play store's search page.
        The token value will be used to fetch next stream data (see parse function).

        :param content: response string.
        :return: pagTok value or None if not found.
        """

        return None
        match = re.search(
            r"'\[.*\\42((?:.(?!\\42))*:S:.*?)\\42.*\]\\n'", content)
        if match:
            return bytes(match.group(1).replace('\\\\', '\\'), 'ascii').decode('unicode-escape')
        else:
            return None

    def parse_app_url(self, response):
        print('parse_app_url-----------------------------------------------------------')
        """
        Parse App detail page.
        """

        if self.is_max_item_reached():
            logging.debug("**** Max Item reached")
            # Stop the crawling if max item reached
            if (self.crawler.engine != None):
                self.crawler.engine.close_spider(self, "Max Item reached")
            return

        loader = AppItemLoader(item=AppItem(), response=response)
        yield loader.load_item()

        self.item_count += 1
        logging.info("**** Item Count: " + str(self.item_count))

    # override
    def parse(self, response):
        print('parse-----------------------------------------------------------')
        pass

    # override
    def closed(self, reason):
        print('closed-----------------------------------------------------------')
        logging.info("**** Spider has stopped. Reason: " + reason +
                     ". Total Scraped Items: " + str(self.item_count))
