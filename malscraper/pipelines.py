# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline

class MalscraperImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item['image_urls']:
            yield scrapy.Request(url, meta = dict(num = item['num']))

    def file_path(self, request, response = None, info = None):
        filename = request.url.split("/")[-1]
        num = request.meta['num']
        return "{0}/{1}".format(num, filename)

    def item_completed(self, results, item, info):
        for ok, x in results:
            if not ok:
                num = x['path'].split("/")[0]
                yield scrapy.Request(x['url'], meta = dict(num = num))
        return item