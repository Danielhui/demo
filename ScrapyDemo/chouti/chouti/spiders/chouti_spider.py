# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector


class ChoutiSpiderSpider(scrapy.Spider):
    name = 'chouti_spider'
    allowed_domains = ['www.chouti.com']
    start_urls = ['http://dig.chouti.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url,callback = self.parse_index)

    def parse_index(self, response):
        #获取cookie，解析cookie
        cookie_dict = {}
        from scrapy.http.cookies import CookieJar
        cookie_jar = CookieJar()
        cookie_jar.extract_cookies(response,response.request)
        for k , v in cookie_jar._cookies.items():
            for i , j in v.items():
                for m,n in j.items():
                    cookie_dict[m] = n.value
        print(cookie_dict)

