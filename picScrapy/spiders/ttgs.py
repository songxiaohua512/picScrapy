# -*- coding:utf-8 -*-
# ! /bin/bash/python3

import json
from scrapy.spiders import Spider
from scrapy.http import Request
from picScrapy.items import AfscrapyItem


class PicSpider(Spider):
    name = "ttgs"  # 定义爬虫名，沱沱工社
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) '
                      'AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    }

    def start_requests(self):
        start_url = 'http://h5.tootoo.cn/cms/variety.html'
        yield Request(start_url, headers=self.headers)

    # 一级页面的处理函数
    def parse(self, response):
        datas = json.loads(response.body.decode('utf-8'))
        for url in datas['result']['content'][0]['items']:
            category_name = url['name']
            cat_id = json.loads(url['PAGE_KEY'])['catIds']
            next_url = 'http://api.tootoo.cn/index.php?' \
                       'r=api/tGoods/appSearch&t=911911911&' \
                       'req_str={"cate_id":"' + cat_id + '","discount":"0","input":"",' \
                       '"special_ids":"","ps":"1,2,7,10021",' \
                       '"page_no":"1","buyer_level":"0","page_size":"100","other":"","price":"","substation":"1",' \
                       '"brand_ids":"","sort":"","scope":"11102","canBeServed":"0"}&_=1504592202363&callback=jsonp1'
            yield Request(next_url, callback=self.parse_data, meta={"cat": category_name})

    # 二级页面的处理函数
    @staticmethod
    def parse_data(response):
        item = AfscrapyItem()
        # 截取jsonp字符里面的json数据部分
        datas = json.loads(response.body[10:-1].decode('utf-8'))
        for data in datas['Result']['Data']['goodsList']:
            item['goods_id'] = data['goodsID']
            item['shop_name'] = "自营"
            item['category_name'] = response.meta["cat"]
            item['title'] = data['goodsTitle']
            item['sales_num'] = data['reviewTotal']
            item['unit'] = ""
            item['price'] = data['skuInfo']['showPrice']
            item['location'] = ""
            yield item
