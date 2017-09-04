# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# -*- coding: utf-8 -*-
from urllib.parse import urlparse
import pymysql
import time
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


def db_handler():
    conn = pymysql.connect(
        host='192.168.0.111',
        user='root',
        passwd='',
        charset='utf8',
        db='scrapy_data',
        use_unicode=True
    )
    conn.autocommit(True)
    return conn


class PicscrapyPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        # 通过meta属性传递title
        return [Request(x, meta={'title': item['title'], 'cat': item['category_name']}) for x in
                item.get(self.images_urls_field, [])]

    # 重写函数，修改了下载图片名称的生成规则
    def file_path(self, request, response=None, info=None):
        if not isinstance(request, Request):
            url = request
        else:
            url = request.url
        url = urlparse(url)
        img_name = url.path.split('/')[5].split('.')[0]
        return request.meta['cat'] + '/' + request.meta['title'] + '/%s.jpg' % img_name


class WebcrawlerScrapyPipeline(object):
    def __init__(self):
        self.db_object = db_handler()
        self.cursor = db_handler().cursor()

    def process_item(self, item, spider):
        if item['category_name'] == "全部":
            return
        try:
            sql = "insert into " + spider.name + "(goods_id, shop_name, " \
                  "category_name, title, sales_num, unit, price, location, created_at)" \
                  "values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            params = (
                item['goods_id'], item['shop_name'], item['category_name'], item['title'],
                item['sales_num'], item['unit'], item['price'], item['location'],
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            )
            self.cursor.execute(sql, params)

        except RuntimeError as e:
            self.db_object.rollback()
            print(e)

        return item
