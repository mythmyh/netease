import os
import sys
s = os.getcwd()
sys.path.append(s[:-16])
sys.path.append(s)
print(sys.path)
from netease.spiders.refer3 import write_packages, delete_packages
write_packages(s)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import pica, inch
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from reportlab.platypus import Paragraph, PageBreak, SimpleDocTemplate, Spacer,Image
import hashlib
import json
import scrapy
from PIL import Image as IM
from scrapy.selector import Selector
from netease.items import PhotoItem
import time
from netease.spiders.db_factory import insert, inspect


write_packages(os.getcwd())
if os.path.exists('site-packages'):
    delete_packages('site-packages')


def get_image_height(filepath):
    c = IM.open(filepath)
    tuple1 = c.size
    info = [tuple1[1], tuple1[0]]
    info = weight_rate(info)

    info = [int(info[0]), int(info[1])]
    return info
# 439 685


def weight_rate(info):
    # info[0] 是高，info[1]是宽

    if info[0] > 685 or info[1] > 439:
        if info[1]/info[0] > 0.71:
            info[0] = info[0]*439/info[1]
            info[0] = info[0]/12
            info[1] = 439/12

            return info
        else:
            info[1] = info[1]*685/info[0]/12
            info[0] = 685/12
            return info
    else:
        info[0] = info[0]/12
        info[1] = info[1]/12
        return info


def build_pdf(files):
    print(os.getcwd())
    registerFont(TTFont('msyh', 'msyh.ttc'))

    # with open(r'news//title.json') as f:
    #     title = json.load(f)
    mystyle = ParagraphStyle(name="user_style", fontName="msyh", leading=30, alignment=TA_LEFT, firstLineIndent=36,
                                 fontSize=18)

    pH = ParagraphStyle(name='Header', fontName='msyh', fontSize=13, leftIndent=20, firstLineIndent=-20,
                        spaceBefore=10, leading=16)
    name = time.strftime("%Y-%m-%d", time.localtime())
    doc = SimpleDocTemplate(name+'.pdf')
    story = []

    with open('index.json') as f:
        infos = json.load(f)
    # column = ['要闻', '地方', '国内', '国际', '独家', '军事', '财经', '科技', '体育', '娱乐', '时尚', '汽车', '房产', '航空', '健康']
    for e in infos.items():
        story.append(Paragraph('<a name ={}></a>{}'.format(hashlib.md5(e[0].encode('utf-8')).hexdigest(), e[0]), pH))
        print(e[1])

        for x in e[1].items():
            md52 = hashlib.md5(x[1].encode('utf-8')).hexdigest()
            if os.path.exists('news/'+md52+'.json'):
                story.append(Paragraph('<a href =#{0}>{1}</a>'.format(md52+'.json', x[0]), pH))
            else:
                print('no')
    story.append(PageBreak())
    os.remove('index.json')

    for b in files:
        with open('news//' + b) as f:
            infos = json.load(f)
        if len(infos[0]) == 0:
            continue
        print(infos[0])

        story.append(Paragraph('<a name ={}></a>{}'.format(b, infos[0]), mystyle))
        story.append(Spacer(1, 2*inch))
        with open('news//'+b) as f:
            content = json.load(f)

            for x in content[2:]:

                if x.endswith('jpg'):
                    try:
                        img2 = Image('images/' + x)
                        t, y = get_image_height('images/' + x)
                        img2.drawHeight = t * pica
                        img2.drawWidth = y * pica
                        story.append(img2)
                    except OSError:
                        pass
                else:
                    story.append(Paragraph(x, style=mystyle))
            story.append(Paragraph("<a href =#{0}>{1}栏目---></a>".format(hashlib.md5(content[1].encode('utf-8')).
                                                                 hexdigest(), '回到' + content[1]), mystyle))
        story.append(PageBreak())
    doc.build(story)


class Netease3Spider(scrapy.Spider):

    name = "netease9"
    start_urls = ['https://news.163.com/']
    custom_settings = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/41.0.2228.0 Safari/537.36",
                       'ITEM_PIPELINES': {'netease.pipes.ImagesPipeline': 1, }
                       }

    def __init__(self, *args, **kwargs):
        super(Netease3Spider, self).__init__(*args, **kwargs)

    def parse(self, response):
        t = response.xpath("//ul[@class='newsdata_list']//div[@class='hidden']").extract()
        j = 0
        l = {}
        column = ['要闻', '地方', '国内', '国际', '独家', '军事', '财经', '科技', '体育', '娱乐', '时尚', '汽车', '房产', '航空', '健康']
        for x in t:
            m = Selector(text=x).xpath('//div/a/text()').extract()
            n = Selector(text=x).xpath('//div/a/@href').extract()
            print(m)
            l[column[j]] = dict(zip(m, n))
            j += 1
        print(l)
        #column = {0: '要闻', 1: '地方', 2: '国内', 3: '国际', 4: '独家', 5: '军事', 6: '财经', 7: '科技', 8: '体育', 9: '娱乐', 10: '时尚', 11: '汽车', 12: '房产', 13: '航空', 14: '健康'}
        # 不要下载的栏目放在targets里，记住是不要下载的
        targets = [1, 5, 8, 11, 13]
        #targets = [x for x in range(1, 14)]

        c = list(l.keys())
        # l结构{0：{title: url}}
        for x in targets:
            l.pop(c[x])
        import copy
        om = copy.deepcopy(l)
        for e in l.items():
            for x in e[1].items():
                if not inspect(x[1]):
                    insert(x[1])
                else:
                    om[e[0]].pop(x[0])
                    pass
        print(om)
        tm = copy.deepcopy(om)
        for x in om.items():
            if len(x[1]) == 0:
                tm.pop(x[0])
        with open('index.json', 'w') as f:
            json.dump(tm, f)
        del l, om
        for e in tm.items():
            for x in e[1].items():

                re = scrapy.Request(x[1], callback=self.parse_item, dont_filter=True, meta={'special': e[0]})
                yield re

    def parse_item(self, response):
        title = response.xpath("//h1//text()").extract()
        s1 = list()
        s1.append(title)
        s1.append(response.meta['special'])
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

        with open('news/'+md53 + '.json', 'w') as f:
            json.dump(s1, f)

    def closed(spider, reason):
        t = os.listdir('news')
        t2 = os.listdir('images')
        if len(t) != 0:
            build_pdf(t)
        for x in t:
            os.remove('news//' + x)
        for x in t2:
            os.remove('images//' + x)
        pass


def run_spider():

    print(os.getcwd())
    process = CrawlerProcess(get_project_settings())
    process.crawl('netease9')
    process.start(stop_after_crawl=True)  # the script will block here until the crawling is finished
    print('hello STOP')
    import sys
    sys.exit(0)


if __name__ == '__main__':

    run_spider()











