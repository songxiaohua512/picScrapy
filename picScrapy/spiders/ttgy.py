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
        # 提取界面所有的符合入口条件的url
        all_urls = response.xpath('//div[@role="tabpanel"]//li')
        if len(all_urls):
            # 遍历获得的url，继续爬取
            for url in all_urls:
                # urljoin生成完整url地址
                category_name = url.xpath('a/text()').extract()[0]
                url = url.xpath('a/@href').extract()[0]
                class_id = re.search('\d+', url).group()
                next_url = "http://m.fruitday.com/ajax/prolist/index"
                yield FormRequest(next_url, formdata={"class_id": class_id, "curr_page": "0"},
                                  callback=self.parse_data,
                                  meta={"cat": category_name, "class_id": class_id, 'page': 0})

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
