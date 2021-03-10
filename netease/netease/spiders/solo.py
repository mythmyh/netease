from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import pica, inch
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from reportlab.platypus import Paragraph, PageBreak, SimpleDocTemplate, Spacer,Image
import os
import hashlib
import json
from scrapy.http import Request
import scrapy
from PIL import Image as IM
from scrapy.selector import Selector
from netease.items import PhotoItem
import time

class NeteaseSpider(scrapy.Spider):

    name = "netease0"
    start_urls = ['https://news.163.com/21/0302/17/G43NJO4300018AP1.html']
    custom_settings = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/41.0.2228.0 Safari/537.36",
                       'ITEM_PIPELINES': {'bilibili.pipes.ImagesPipeline': 1, }
                       }

    def __init__(self, *args, **kwargs):
        super(NeteaseSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        title = response.xpath("//h1//text()").extract()
        s1 = list()
        s1.append(title)
        k = response.request.url
        md53 = hashlib.md5(k.encode('utf-8')).hexdigest()

        # 核心思想去掉一段文字的<a></a>链接

        def delete_links(v):

            m = len(v)
            k = v.find("<a")
            if k != -1:
                c = v[k:m]
                n = c.find('>')
                j = k + n + 1
                v = v.replace(v[k:j], "")
                return delete_links(v)
            else:
                while "</a>" in v:
                    v = v.replace("</a>", "")
                sa = v

                return sa

        t = response.xpath("//div[@class='post_body']/p")
        post_info = response.xpath("//div[@class='post_info']").extract()[0]
        post_info2 = delete_links(post_info)
        content_info = Selector(text=post_info2).xpath("//text()").extract()[0]

        content_info = content_info.replace('举报', '')

        s1.append(response.url)
        if len(content_info) >= 1:
            s1.append(content_info)

        for x in t:
            img_src = x.xpath('img/@src').extract()

            if len(img_src) > 0:
                url = x.xpath('img/@src').extract()[0]
                print(url)
                md51 = hashlib.md5(url.encode('utf-8')).hexdigest()
                s1.append(md51 + '.jpg')
                image2 = PhotoItem()
                image2['image_urls'] = [url]
                yield image2

            a = x.xpath("a/text()")
            if len(a) != 0:
                o1 = delete_links(x.extract())
                content = Selector(text=o1).xpath("//p//text()").extract()[0]
                s1.append(content)
            else:
                t = x.xpath("text()").extract()

                if len(t) != 0:
                    s1.append(t[0])

        print(s1)

    def closed(spider, reason):
        pass

def run_spider():

    print(os.getcwd())
    process = CrawlerProcess(get_project_settings())
    process.crawl('netease0')
    process.start(stop_after_crawl=True)  # the script will block here until the crawling is finished
    print('hello STOP')
    import sys
    sys.exit(0)


if __name__ == '__main__':

    run_spider()











