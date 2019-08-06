# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ImageItem(scrapy.Item):
    # define the fields for your item here like:
    image_urls = scrapy.Field()
    num = scrapy.Field()
    max_downloads = scrapy.Field()
    images = scrapy.Field()
