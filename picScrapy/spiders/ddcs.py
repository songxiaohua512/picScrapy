# -*- coding:utf-8 -*-
# ! /bin/bash/python3

import json
from scrapy.spiders import Spider
from scrapy.http import Request
from picScrapy.items import AfscrapyItem


class PicSpider(Spider):
    name = "ddcs"  # 定义爬虫名，多点超市
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36',
    }

    def start_requests(self):

        start_url = 'https://gatewx.dmall.com/customersite/index?' \
                    'param={"pairs":"1-0-108","bizType":"1"}&' \
                    'token=&source=2&tempid=C7AB48CAE0E000028115E360BB871D77&pubParam={}&_=1504512439909'
        yield Request(start_url, headers=self.headers)

    # 一级页面的处理函数
    def parse(self, response):
        # 提取界面所有的符合入口条件的url
        all_cat = json.loads(response.body.decode('utf-8'))
        # 遍历获得的url，继续爬取
        for cat in all_cat['data']['categoryInfo']['categorys'][1:]:
            # urljoin生成完整url地址
            for cmCatId in cat['childCmCategories']:
                for cmCatIdId in cmCatId['childCmCategories']:
                    next_url = 'https://gatewx.dmall.com/customersite/searchWareByCategory?' \
                               'param={"pageNum":1,"pageSize":100,"venderId":"1","storeId":"108",' \
                               '"sort":"1","categoryId":' + str(cmCatIdId['cmCatId']) + ',' \
                               '"categoryLevel":3,"cateSource":1,"bizType":"1"}&token=&source=2' \
                               '&tempid=C7AB48CAE0E000028115E360BB871D77&pubParam={}&_=1504515435126'
                    yield Request(next_url, callback=self.parse_data)

    # 二级页面的处理函数
    @staticmethod
    def parse_data(response):
        item = AfscrapyItem()
        datas = json.loads(response.body.decode('utf-8'))
        for data in datas['data']['list']:
            item['goods_id'] = data['skuId']
            item['shop_name'] = data['shop']
            item['category_name'] = data['secondCatName']
            item['title'] = data['title']
            item['sales_num'] = 0
            item['unit'] = ""
            item['price'] = data['promotionInfo']['promotionPrice'] / 100
            item['location'] = ""
            yield item
