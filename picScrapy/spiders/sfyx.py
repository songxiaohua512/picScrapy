# -*- coding:utf-8 -*-
# ! /bin/bash/python3

import re
import json
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.http import FormRequest
from picScrapy.items import AfscrapyItem


class PicSpider(Spider):
    name = "sfyx"  # 定义爬虫名，顺丰优选
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) '
                      'AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    }

    def start_requests(self):

        start_url = 'https://m.sfbest.com/category'
        yield Request(start_url, headers=self.headers)

    # 一级页面的处理函数
    def parse(self, response):
        parent_path = response.xpath('//ul[@class="category-tab clearfix"]/a')
        for path in parent_path:
            category_name = re.search('[\u4E00-\u9FA5]+', path.xpath('.//div[@class="category-name"]/text()').extract()[0]).group(0)
            next_url = path.xpath("./@href").extract()[0]
            yield Request(next_url, callback=self.parse_data, meta={"cat": category_name})

    # 二级页面的处理函数
    def parse_data(self, response):
        item = AfscrapyItem()
        datas = response.xpath('//div[@class="p-list clearfix"]')
        for data in datas:
            item['goods_id'] = data.xpath('.//a[@id="add_cart"]/@productid').extract()[0]
            item['category_name'] = response.meta["cat"]
            name = data.xpath('.//div[@class="p-name"]/text()')
            if len(name) == 2:
                item['shop_name'] = data.xpath('.//div[@class="p-name"]/span/text()').extract()[0]
                item['title'] = re.search('([\u4E00-\u9FA5]+[A-Za-z]*\s?)+',
                                          data.xpath('.//div[@class="p-name"]/text()').extract()[1]).group()
            else:
                item['shop_name'] = re.search('[\u4E00-\u9FA5]+',
                                              data.xpath('.//div[@class="p-name"]/text()').extract()[0]).group()
                item['title'] = re.search('([\u4E00-\u9FA5]+[A-Za-z]*\s?)+',
                                          data.xpath('.//div[@class="p-name"]/text()').extract()[0]).group()
            sales_num = data.xpath('.//div[@class="p-gray-info"]/text()').extract()
            if len(sales_num) > 1:
                item['sales_num'] = re.search(r'\d+', sales_num[1]).group()
            else:
                item['sales_num'] = 0

            unit = data.xpath('.//div[@class="p-name"]/text()').extract()
            if len(unit) > 1:
                item['unit'] = re.search('\d+.+', unit[1]).group()
            else:
                item['unit'] = ""
            item['price'] = data.xpath('.//div[@class="p-price fl"]/span/text()').extract()[0] + \
                data.xpath('.//div[@class="p-price fl"]/text()').extract()[1]
            item['location'] = re.search('[\u4E00-\u9FA5]*',
                                         data.xpath('.//div[@class="p-gray-info"]/text()').extract()[0]).group()
            yield item
            next_page = re.search('pageNo=(\d+)', response.url).group(1)
            next_page = 'pageNo='+str(int(next_page)+1)
            next_url = re.sub('pageNo=\d+', next_page, response.url)
            yield Request(next_url, callback=self.parse_data, meta={"cat": response.meta["cat"]})
