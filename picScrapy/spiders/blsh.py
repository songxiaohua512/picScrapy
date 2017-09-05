# -*- coding:utf-8 -*-
# ! /bin/bash/python3

import re
import json
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.http import FormRequest
from picScrapy.items import AfscrapyItem


class PicSpider(Spider):
    name = "blsh"  # 定义爬虫名，本来生活
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36',
    }

    def start_requests(self):
        start_url = 'http://www.benlai.com/'
        yield Request(start_url, headers=self.headers)

    # 一级页面的处理函数
    def parse(self, response):
        all_urls = response.xpath('//div[@class="tit_sort"]//dl')
        if len(all_urls):
            for url in all_urls:
                category_name = url.xpath('./dt/a/text()').extract()[0]
                next_urls = url.xpath('.//em//a/@href').extract()
                for next_url in next_urls:
                    class_id = re.search("list-(\d+)-(\d+)-(\d+)", next_url)
                    c1 = class_id.group(1)
                    c2 = class_id.group(2)
                    c3 = class_id.group(3)
                    next_url = "http://www.benlai.com/NewCategory/GetLuceneProduct"
                    yield FormRequest(next_url, formdata={"c1": c1, "c2": c2, "c3": c3, "page": "1"},
                                      callback=self.parse_data,
                                      meta={"cat": category_name, "c1": c1, "c2": c2, "c3": c3, "page": "1"})

    # 二级页面的处理函数
    def parse_data(self, response):
        item = AfscrapyItem()
        datas = json.loads(response.body.decode('utf-8'))
        for data in datas['ProductList']:
            item['goods_id'] = data['ProductSysNo']
            item['shop_name'] = "自营"
            item['category_name'] = response.meta["cat"]
            item['title'] = data['ProductName']
            item['sales_num'] = 0
            item['unit'] = ""
            item['price'] = data['ProductNowPrice']
            item['location'] = ""
            yield item
        if len(datas['ProductList']):
            next_page = int(response.meta["page"]) + 1
            yield FormRequest(response.url,
                              formdata={"c1": response.meta['c1'], "c2": response.meta['c2'], "c3": response.meta['c3'],
                                        "page": str(next_page)},
                              callback=self.parse_data,
                              meta={"cat": response.meta["cat"], "c1": response.meta['c1'], "c2": response.meta['c2'],
                                    "c3": response.meta['c3'], "page": str(next_page)})
