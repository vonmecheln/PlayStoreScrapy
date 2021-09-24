### Note: this project isn't maintained anymore and most likely doesn't work anymore with the latest playstore.

PlayStoreScrapy
===============

A showcase of Google PlayStore Scraper built on top of Python + Scrapy Framework.

It will scrape the android apps data into CSV file based on search keyword inputs.

Requirements
============

 * Python v2.7.x
 * Scrapy


How to run
==========

    $ cd PlayStoreScrapy
    $ scrapy crawl playstorescrapy -a keywords=<your_keywords>

You can also supply multiple keywords separated by comma:

    $ scrapy crawl playstorescrapy -a keywords=browser,game,chat

Additional options:

    -a max_item=<number>          Specify maximum number of scraped items (default=0)
    -a output=<filename>          Specify output filename path (default=item.csv)
    -a download_delay=<number>    Specify download delay in seconds (default=0)
    -a email=<email>              Specify login email
    -a "password=<password>"      Specify login password (note: the double-quotes is required)

