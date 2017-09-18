# -*- coding:utf-8 -*-
# ! /bin/bash/python3

import json
import re
import requests
from scrapy.spiders import Spider
from scrapy.http import Request
from urllib.parse import urljoin
from picScrapy.items import AfscrapyItem


class PicSpider(Spider):
    name = "zlwm"  # 定义爬虫名，中粮我买
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.79 Safari/537.36',
    }

    def start_requests(self):
        start_url = 'http://www.womai.com/index-31000-0.htm'
        yield Request(start_url, callback=self.parse, headers=self.headers)

    # 一级页面的处理函数
    def parse(self, response):
        datas = response.xpath('//li[@class="kinds"]')
        for url in datas:
            category_name = url.xpath('./h3/a[1]/text()').extract()[0]
            next_urls = url.xpath('.//li[@class="sub_kind"]/a/@href').extract()
            for next_url in next_urls:
                next_url = urljoin(response.url, next_url)
                yield Request(next_url, callback=self.parse_data, meta={"cat": category_name}, headers=self.headers)

    # 二级页面的处理函数
    @staticmethod
    def parse_data(response):
        item = AfscrapyItem()
        # 截取jsonp字符里面的json数据部分
        datas = response.xpath('//div[@class="product-list"]/ul/li')
        for data in datas:
            item['goods_id'] = data.xpath('./@data-productid').extract()[0]
            title = data.xpath('.//div[@class="list-title"]/p/a/text()').extract()[0]
            shop_name = re.search('【(.+)】', title)
            if shop_name:
                item['shop_name'] = shop_name.group(1)
            else:
                item['shop_name'] = ''
            item['category_name'] = response.meta["cat"]
            item['title'] = re.search('\S+\s*\S+', title).group()
            item['sales_num'] = data.xpath('.//span[@class="evaluated"]/a/em/text()').extract()[0]
            item['unit'] = re.search('\d+.*', title).group()
            # item['price'] = data.xpath('.//div[@class="price"]/b/text()')
            product_url = 'http://price.womai.com/PriceServer/open/productlist.do?' \
                          'usergroupid=100&ids='+item['goods_id']+'&mid=0&cityid=31000&picType=0&sellable=true' \
                          '&properties=title&pics=pic60&prices=buyPrice&callback=jsonp'
            response_new = requests.get(product_url)
            if (response_new.status_code == 200) and response_new.text:
                res = re.match('jsonp\((.+)\)', response_new.text).group(1)
                result = json.loads(res, encoding='utf-8')
                if len(result['result']):
                    item['price'] = result['result'][0]['price']['buyPrice']['priceValue']
                else:
                    item['price'] = 0.0
            else:
                item['price'] = 0.0
            item['location'] = ""
            yield item
