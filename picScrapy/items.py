# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PicscrapyItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    title = scrapy.Field()
    category_name = scrapy.Field()


class TccscrapyItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    sales = scrapy.Field()
    location = scrapy.Field()
    seller = scrapy.Field()
