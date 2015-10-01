# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from datetime import datetime
import re
import scrapy
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Join, MapCompose, Compose, TakeFirst
from scraper.selector import Selector


class ParseDevLinks(object):
    def __init__(self, text):
        self.text = text

    def __call__(self, response):
        nodes = Selector(xpath=AppItem.APP_DEV_LINKS).get_element_list(response)
        for node in nodes:
            text = Selector.get_text(node).lower()
            if self.text == "email" and self.text in text:
                return Selector.get_attribute(node, "href").replace("mailto:", "").strip()
            elif self.text == "website" and self.text in text:
                return self.extract_url_from_google_url(Selector.get_attribute(node, "href"))
            elif self.text == "privacy" and self.text in text:
                return self.extract_url_from_google_url(Selector.get_attribute(node, "href"))

    @staticmethod
    def extract_url_from_google_url(url):
        match = re.search(r"http[s]*://www\.google\.com/url\?q=(http[s]*://.+)&sa=.*", url)
        if match:
            return match.group(1)
        else:
            return ""


class AppItemLoader(ItemLoader):
    default_output_processor = Compose(TakeFirst(), lambda value: value.strip())

    # override
    def load_item(self):
        for field_name, attr in self.item.fields.items():
            xpath = attr.get('xpath')
            css = attr.get('css')
            callback = attr.get('callback')

            if xpath:
                self.add_xpath(field_name, xpath)

            elif css:
                self.add_css(field_name, css)

            elif callback:
                self.add_value(field_name, callback(self.context.get('response')))

        return super(AppItemLoader, self).load_item()


class AppItem(scrapy.Item):
    APP_URL_PREFIX = 'https://play.google.com'

    # XPATH
    APP_NAME = "//div[@class='info-container']/div[@class='document-title' and @itemprop='name']/div/text()"
    APP_DEV = "//div[@class='info-container']/div[@itemprop='author']/a/span[@itemprop='name']/text()"
    APP_TOP_DEV = "//meta[@itemprop='topDeveloperBadgeUrl']/@content"
    APP_DEV_URL = "//div[@class='info-container']/div[@itemprop='author']/meta[@itemprop='url']/@content"
    APP_CATEGORY = "//div/a[@class='document-subtitle category']/@href"
    APP_PRICE = "//span[@itemprop='offers' and @itemtype='http://schema.org/Offer']/meta[@itemprop='price']/@content"
    APP_COVER_IMG = "//div[@class='details-info']/div[@class='cover-container']/img[@class='cover-image']/@src"
    APP_DESCRIPTION = "//div[@class='show-more-content text-body' and @itemprop='description']//text()"
    APP_SCORE_VALUE = "//div[@class='rating-box']/div[@class='score-container']/meta[@itemprop='ratingValue']/@content"
    APP_SCORE_COUNT = "//div[@class='rating-box']/div[@class='score-container']/meta[@itemprop='ratingCount']/@content"
    APP_FIVE_STARS = "//div[@class='rating-histogram']/div[@class='rating-bar-container five']/span[@class='bar-number']/text()"
    APP_FOUR_STARS = "//div[@class='rating-histogram']/div[@class='rating-bar-container four']/span[@class='bar-number']/text()"
    APP_THREE_STARS = "//div[@class='rating-histogram']/div[@class='rating-bar-container three']/span[@class='bar-number']/text()"
    APP_TWO_STARS = "//div[@class='rating-histogram']/div[@class='rating-bar-container two']/span[@class='bar-number']/text()"
    APP_ONE_STARS = "//div[@class='rating-histogram']/div[@class='rating-bar-container one']/span[@class='bar-number']/text()"
    APP_PUBLISH_DATE = "//div[@class='meta-info']/div[@itemprop='datePublished']/text()"
    APP_SIZE = "//div[@class='meta-info']/div[@itemprop='fileSize']/text()"
    APP_INSTALLS = "//div[@class='content' and @itemprop='numDownloads']/text()"
    APP_VERSION = "//div[@class='content' and @itemprop='softwareVersion']/text()"
    APP_OS_REQUIRED = "//div[@class='content' and @itemprop='operatingSystems']/text()"
    APP_CONTENT_RATING = "//div[@class='content' and @itemprop='contentRating']/text()"
    APP_IAP_MESSAGE = "//div[@class='info-container']/div[@class='inapp-msg']/text()"
    APP_IAP_PRICE = "//div[@class='details-section-contents']//div[@class='meta-info'][div[@class='title']/text()[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'in-app')]]/div[@class='content']/text()"
    APP_DEV_LINKS = "//div[@class='content contains-text-link']/a[@class='dev-link']"

    # Fields
    Url = scrapy.Field(callback=lambda response: response.url.replace("&hl=en", ""))
    ScrapedDate = scrapy.Field(callback=lambda response: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    Name = scrapy.Field(xpath=APP_NAME)
    Developer = scrapy.Field(xpath=APP_DEV)

    IsTopDeveloper = scrapy.Field(
        xpath=APP_TOP_DEV,
        input_processor=lambda value: "True" if value else "False"
    )

    DeveloperURL = scrapy.Field(
        xpath=APP_DEV_URL,
        output_processor=Compose(
            TakeFirst(),
            lambda value: AppItem.APP_URL_PREFIX + value if value else ""
        )
    )

    PublicationDate = scrapy.Field(
        xpath=APP_PUBLISH_DATE,
        output_processor=Compose(
            TakeFirst(),
            lambda value: str(datetime.strptime(value.replace(",", "").strip(), "%B %d %Y").date()) if value else ""
        )
    )

    Category = scrapy.Field(
        xpath=APP_CATEGORY,
        output_processor=Compose(
            TakeFirst(),
            lambda value: value.split("/")[-1] if value else ""
        )
    )

    IsFree = scrapy.Field(
        xpath=APP_PRICE,
        output_processor=Compose(
            TakeFirst(),
            lambda value: "True" if value == "0" else "False"
        )
    )

    Price = scrapy.Field(
        xpath=APP_PRICE,
        output_processor=Compose(
            TakeFirst(),
            lambda value: "" if value == "0" else value
        )
    )

    CoverImageUrl = scrapy.Field(xpath=APP_COVER_IMG)
    Description = scrapy.Field(
        xpath=APP_DESCRIPTION,
        output_processor=Compose(
            Join('\n'),
            lambda value: value.strip()
        )
    )

    ReviewScore = scrapy.Field(xpath=APP_SCORE_VALUE)
    ReviewTotal = scrapy.Field(xpath=APP_SCORE_COUNT)
    FiveStarsReviews = scrapy.Field(xpath=APP_FIVE_STARS)
    FourStarsReviews = scrapy.Field(xpath=APP_FOUR_STARS)
    ThreeStarsReviews = scrapy.Field(xpath=APP_THREE_STARS)
    TwoStarsReviews = scrapy.Field(xpath=APP_TWO_STARS)
    OneStarReviews = scrapy.Field(xpath=APP_ONE_STARS)
    AppSize = scrapy.Field(xpath=APP_SIZE)
    Installs = scrapy.Field(xpath=APP_INSTALLS)
    CurrentVersion = scrapy.Field(xpath=APP_VERSION)
    MinimumOSVersion = scrapy.Field(xpath=APP_OS_REQUIRED)
    ContentRating = scrapy.Field(xpath=APP_CONTENT_RATING)

    HaveInAppPurchases = scrapy.Field(
        xpath=APP_IAP_MESSAGE,
        input_processor=lambda value: "True" if value else "False"
    )

    InAppPriceRange = scrapy.Field(xpath=APP_IAP_PRICE)
    DeveloperEmail = scrapy.Field(callback=ParseDevLinks("email"))
    DeveloperWebsite = scrapy.Field(callback=ParseDevLinks("website"))
    DeveloperPrivacyPolicy = scrapy.Field(callback=ParseDevLinks("privacy"))
