# -*- coding:utf-8 -*-
# ! /bin/bash/python3

import re
import json
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.http import FormRequest
from picScrapy.items import AfscrapyItem


class PicSpider(Spider):
    name = "ttgy"  # 定义爬虫名，天天果园
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36',
    }

    def start_requests(self):

        start_url = 'http://m.fruitday.com/cat'
        yield Request(start_url, headers=self.headers)

    # 一级页面的处理函数
    def parse(self, response):
        parent_path = response.xpath('//section[@id="m-category"]')
        for i in range(1, 9):
            category_name = parent_path.xpath("./ul/li["+str(i)+"]/a/text()").extract()[0]
            all_urls = parent_path.xpath(".//div/div["+str(i)+"]/ul/li/a/@href").extract()
            for url in all_urls:
                class_id = re.search('\d+', url).group()
                next_url = "http://m.fruitday.com/ajax/prolist/index"
                yield FormRequest(next_url, formdata={"class_id": class_id, "curr_page": "0"},
                                  callback=self.parse_data,
                                  meta={"cat": category_name, "class_id": class_id, 'page': "0"})

    # 二级页面的处理函数
    def parse_data(self, response):
        item = AfscrapyItem()
        datas = json.loads(response.body.decode('utf-8'))
        for data in datas['msg']:
            item['goods_id'] = data['id']
            item['shop_name'] = "自营"
            item['category_name'] = response.meta["cat"]
            item['title'] = data['product_name']
            item['sales_num'] = 0
            item['unit'] = data['volume']
            item['price'] = data['price']
            item['location'] = ""
            yield item
            next_page = int(response.meta['page']) + 1
            yield FormRequest(response.url, formdata={"class_id": response.meta["class_id"], "curr_page": str(next_page)},
                              callback=self.parse_data,
                              meta={"cat": response.meta["cat"],
                                    "class_id": response.meta["class_id"], "page": next_page})
