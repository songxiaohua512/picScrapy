# -*- coding:utf-8 -*-
# ! /bin/bash/python3

import json
from scrapy.spiders import Spider
from scrapy.http import Request
from picScrapy.items import AfscrapyItem


class PicSpider(Spider):
    name = "mryx"  # 定义爬虫名，每日优鲜
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) '
                      'AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
        'Content-Type': 'application/json;charset=UTF-8',
        'platform': 'web',
        'Referer': 'https://as-vip.missfresh.cn/frontend/',
        'version': '3.7.0.1',
        'x-region': '{"station_code":"MRYX|mryx_bj_gt","address_code":110105}',
        'X-Tingyun-Id': 'Q1KLryMuSto;r=98015917'
    }

    def start_requests(self):
        start_url = 'https://as-vip.missfresh.cn/v2/product/home/index?' \
                    'device_id=e97030a623d921f26d1db49c3288760d&env=web&' \
                    'fromSource=zhuye&platform=web&uuid=e97030a623d921f26d1db49c3288760d&version=3.7.0.1'
        yield Request(start_url, method="POST", body=json.dumps({"lat": 39.92147, "lng": 116.44311}),
                      headers=self.headers)

    # 一级页面的处理函数
    def parse(self, response):
        datas = json.loads(response.body.decode('utf-8'))
        for url in datas['category_list']:
            category_name = url['name']
            cat_id = url['internal_id']
            next_url = 'https://as-vip.missfresh.cn/v3/product/category/'+cat_id+'?' \
                       'device_id=e97030a623d921f26d1db49c3288760d&env=web&' \
                       'fromSource=zhuye&platform=web&uuid=e97030a623d921f26d1db49c3288760d&version=3.7.0.1'
            yield Request(next_url, callback=self.parse_data, meta={"cat": category_name}, headers=self.headers)

    # 二级页面的处理函数
    @staticmethod
    def parse_data(response):
        item = AfscrapyItem()
        # 截取jsonp字符里面的json数据部分
        datas = json.loads(response.body.decode('utf-8'))
        for data in datas['products']:
            if 'vip_product' not in data.keys():
                continue
            item['goods_id'] = data['sku']
            item['shop_name'] = "自营"
            item['category_name'] = response.meta["cat"]
            item['title'] = data['name']
            item['sales_num'] = 0
            item['unit'] = data['unit']
            item['price'] = data['vip_price'] / 100
            item['location'] = ""
            yield item
