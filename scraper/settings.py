# -*- coding: utf-8 -*-

# Scrapy settings for scrapy project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'playstorescrapy'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scraper (+http://www.yourdomain.com)'

#DOWNLOAD_DELAY = 1

LOG_LEVEL = 'INFO'

ITEM_PIPELINES = {'scraper.pipelines.CSVPipeline': 300}

EXPORT_FIELDS = [
    "Url",
    "ScrapedDate",
    "Name",
    "Developer",
    "IsTopDeveloper",
    "DeveloperURL",
    "PublicationDate",
    "Category",
    "IsFree",
    "Price",
    "CoverImageUrl",
    "Description",
    "ReviewScore",
    "ReviewTotal",
    "FiveStarsReviews",
    "FourStarsReviews",
    "ThreeStarsReviews",
    "TwoStarsReviews",
    "OneStarReviews",
    "AppSize",
    "Installs",
    "CurrentVersion",
    "MinimumOSVersion",
    "ContentRating",
    "HaveInAppPurchases",
    "InAppPriceRange",
    "DeveloperEmail",
    "DeveloperWebsite",
    "DeveloperPrivacyPolicy",
]