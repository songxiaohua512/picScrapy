# -*- coding:utf-8 -*-
# ! /bin/bash/python3
import re
from scrapy.spiders import Spider
from scrapy.http import Request
from picScrapy.items import AfscrapyItem


class PicSpider(Spider):
    name = "cbsh"  # 定义爬虫名，春播商城
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36',
    }

    def start_requests(self):
        start_url = 'http://www.chunbo.com/'
        yield Request(start_url, headers=self.headers)

    # 一级页面的处理函数
    def parse(self, response):
        all_urls = response.xpath('//ul[@class="nav_all_slide"]//li')
        for url in all_urls:
            category_name = url.xpath('.//a/text()').extract()[1].\
                replace(' ', '').replace('\n', '')
            next_urls = url.xpath('.//dd/a/@href').extract()
            for next_url in next_urls:
                yield Request(next_url, callback=self.parse_data, meta={"cat": category_name})

    # 二级页面的处理函数
    @staticmethod
    def parse_data(response):
        item = AfscrapyItem()
        datas = response.xpath('//div[@id="product_list"]//li')
        for data in datas:
            item['goods_id'] = data.xpath('.//p[@class="fav"]/@data-pid').extract()[0]
            item['shop_name'] = "自营"
            item['category_name'] = response.meta["cat"]
            item['title'] = data.xpath('.//h4/a/text()').extract()[0]
            item['sales_num'] = 0
            item['unit'] = data.xpath('.//p[@class="num"]/text()').extract()[0]
            item['price'] = re.search('\d+.\d+', data.xpath('.//p[@class="price"]/strong/text()').extract()[0]).group()
            item['location'] = ""
            yield item
