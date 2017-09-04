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


# 商品数据
class AfscrapyItem(scrapy.Item):
    goods_id = scrapy.Field()
    shop_name = scrapy.Field()
    category_name = scrapy.Field()
    title = scrapy.Field()
    sales_num = scrapy.Field()
    unit = scrapy.Field()
    price = scrapy.Field()
    location = scrapy.Field()
