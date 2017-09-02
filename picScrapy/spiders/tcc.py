# -*- coding:utf-8 -*-
# ! /bin/bash/python3

from urllib.parse import urlparse
from scrapy.spiders import Spider
from scrapy.http import Request
from picScrapy.items import TccscrapyItem


class PicSpider(Spider):
    name = "tcc"  # 定义爬虫名
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0',
    }

    def start_requests(self):
        start_url = "https://chi.taobao.com/"
        yield Request(start_url, headers=self.headers)

    # 一级页面的处理函数
    def parse(self, response):
        # 提取界面所有的符合入口条件的url
        all_urls = response.xpath(
            '//div[@class="sub-lists item-links"]/span')
        if len(all_urls):
            # 遍历获得的url，继续爬取
            for url in all_urls:
                cat = url.xpath("a/text()").extract()
                url = url.xpath("a/@href").extract()
                if len(cat):
                    cat = cat[0]
                else:
                    cat = ""

                if len(url):
                    url = url[0]
                else:
                    break
                url = urlparse(url)
                next_url = "https://list.taobao.com" \
                           + url[2] + "?" + url[4] + "&json=on&pSize=95&_ksTS=1504345515312_48"

                yield Request(next_url, callback=self.parse_goods,
                              meta={'cat': cat, 'url': next_url}, headers=self.headers)

    # 二级页面的处理函数
    @staticmethod
    def parse_goods(response):
        # 提取符合条件的url
        # 遍历获得的url，继续爬取
        for goods in response.itemList:
            item = TccscrapyItem()
            # 提取页面符合条件的图片地址
            item['name'] = goods['title']
            item['price'] = goods['currentPrice']
            item['sales'] = goods['tradeNum']
            item['seller'] = goods['nick']
            item['location'] = goods['loc']
            yield item
