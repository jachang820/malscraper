# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline

class MalscraperImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        count = len(item['image_urls'])
        if count > item['max_downloads']:
            count = item['max_downloads']
        for i in range(count):
            url = item['image_urls'][i]
            yield scrapy.Request(url, meta = dict(num = item['num']))

    def file_path(self, request, response = None, info = None):
        filename = request.url.split("/")[-1]
        num = request.meta['num']
        return "{0}/{1}".format(num, filename)