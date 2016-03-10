# coding:utf-8
from scrapy.spiders import BaseSpider
from scrapy.http import Request
from scrapy.selector import Selector
import sys, json, re
from mkspider.items import MkspiderItem

reload(sys)
sys.setdefaultencoding('utf-8')


class mkspiders(BaseSpider):
    name = "mkspiders"
    tag = 'fe'
    base_page = 'http://www.imooc.com/course/list?c=' + tag + '&page='
    start_urls = []
    allowed_domains = ['www.imooc.com', '']

    def __init__(self):
        for i in range(1, 10):
            url = self.base_page + str(i)
            self.start_urls.append(url)
            i += 1

    def parse(self, response):
        print response.url
        print '========================================'
        page_course_css = Selector(text=response.body).css('div.js-course-lists li.course-one ').extract()
        for item in page_course_css:
            meta = MkspiderItem()
            href = Selector(text=item).css('a::attr(href)').extract()[0]
            if href:
                id = href[str(href).rindex('/') + 1:]
                href = "http://www.imooc.com/learn/" + href[str(href).rindex('/') + 1:]
                meta['pLessID'] = id
                meta['pLessHref'] = href
            title = Selector(text=item).css('a h5 span::text').extract()[0]
            meta['pLessName'] = str(title).replace('"', '').replace('\'', '')
            yield Request(href, callback=self.parse_course, meta={'meta': meta})

    def parse_course(self, response):
        meta = response.meta['meta']
        course_css = Selector(text=response.body).css('ul.video li').extract()
        for course in course_css:
            href = Selector(text=course).css('a::attr(href)').extract()[0]
            id = href[str(href).rindex('/') + 1:]
            name = str(Selector(text=course).css('a::text').extract()[0]).strip()
            try:
                name.index('(')
                name = name[:name.index('(') - 1].strip()
            except:
                pass
            print id, name, href
            meta['LessID'] = id
            meta['LessHref'] = href
            meta['LessName'] = name
            url = 'http://www.imooc.com/course/ajaxmediainfo/?mid=' + id + '&mode=flash'
            meta['LessVideo'] = url
            meta['VideoHref'] = ''
            yield Request(url, callback=self.get_download, meta={'meta': meta})

    def get_download(self, response):
        mkitem = response.meta['meta']
        video_json = json.loads(response.body)['data']['result']['mpath']
        for item in video_json:
            if 'h.mp4' in str(item).lower():
                mkitem['VideoHref'] = item
            else:
                mkitem['VideoHref'] = ''
        yield mkitem
