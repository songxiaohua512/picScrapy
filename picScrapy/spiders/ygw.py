# -*- coding:utf-8 -*-
# ! /bin/bash/python3

import re
from scrapy.spiders import Spider
from scrapy.http import Request
from picScrapy.items import AfscrapyItem


class PicSpider(Spider):
    name = "ygw"  # 定义爬虫名，依谷网
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36',
    }

    def start_requests(self):

        start_url = 'http://www.egu365.com/eguHead.action?id=1&style=0'
        yield Request(start_url, headers=self.headers)

    # 一级页面的处理函数
    def parse(self, response):
        all_urls = response.xpath('//div[@class="all-sort-list"]/div')
        for url in all_urls:
            category_name = url.xpath(".//h3/a/text()").extract()[0]
            next_urls = url.xpath(".//em/a/@href").extract()
            for next_url in next_urls:
                yield Request('http://www.egu365.com'+next_url, callback=self.parse_data, meta={"cat": category_name})

    # 二级页面的处理函数
    @staticmethod
    def parse_data(response):
        item = AfscrapyItem()
        datas = response.xpath('//div[@class="list-nr-ri-content"]//li')
        for data in datas:
            item['goods_id'] = data.xpath('.//div[@class="he-view"]/a/@goods').extract()[0]
            item['shop_name'] = "自营"
            item['category_name'] = response.meta["cat"]
            item['title'] = data.xpath('.//div[@class="wz"]/a/text()').extract()[0]
            item['sales_num'] = 0
            item['unit'] = ""
            item['price'] = re.search('(\d+).(\d+)', data.xpath('.//div[@class="list-price"]/b/text()').extract()[0]).group()
            item['location'] = ""
            yield item
