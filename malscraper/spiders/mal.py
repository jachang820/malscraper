# -*- coding: utf-8 -*-
import scrapy


class MalSpider(scrapy.Spider):
    name = 'mal'
    allowed_domains = ['myanimelist.net']
    start_urls = ['http://myanimelist.net/']

    def parse(self, response):
        pass
