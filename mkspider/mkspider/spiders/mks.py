# coding:utf-8
from scrapy.spiders import BaseSpider
from scrapy.http import Request
from scrapy.selector import Selector
import sys, json, re, requests
from mkspider.items import MkspiderItem

reload(sys)
sys.setdefaultencoding('utf-8')


class mkspiders(BaseSpider):
    name = "mkss"
    tag = 'fe'
    tag_total_page = 9
    base_page = 'http://www.imooc.com/course/list?c=' + tag + '&page='
    start_urls = []
    allowed_domains = ['www.imooc.com', '']

    def __init__(self):
        pages_content = [(requests.get(self.base_page + str(i)).text) for i in range(1, self.tag_total_page + 1)]
        for content in pages_content:
            css_course = Selector(text=content).css('div.js-course-lists li.course-one').extract()
            for course in css_course:
                href = str(Selector(text=course).css('a::attr(href)').extract()[0])
                id = href[href.rindex('/') + 1:]
                learnHref = 'http://www.imooc.com/learn/' + id
                self.start_urls.append(learnHref)

    def parse(self, response):
        pLessHref = str(response.url)
        pLessID = pLessHref[pLessHref.rindex('/') + 1:]
        course_css = Selector(text=response.body).css('ul.video li a.studyvideo').extract()
        for course in course_css:
            meta = {}
            href = str(Selector(text=course).css('::attr(href)').extract()[0])
            id = href[str(href).rindex('/') + 1:]
            name = Selector(text=course).css('::text').extract()[0]
            video_url = 'http://www.imooc.com/course/ajaxmediainfo/?mid=' + id + '&mode=flash'
            try:
                name.index('(')
                name = name[:name.index('(') - 1].strip()
            except:
                pass
            meta['pLessID'] = pLessID
            meta['pLessHref'] = pLessHref
            meta['pLessName'] = ''
            meta['LessID'] = id
            meta['LessName'] = name
            meta['LessHref'] = href
            meta['LessVideo'] = video_url
            yield Request(video_url, callback=self.get_download, meta={'meta': meta})

    def get_download(self, response):
        mkitem = MkspiderItem()
        mkitem = response.meta['meta']
        video_json = json.loads(response.body)['data']['result']['mpath']
        try:
            for item in video_json:
                if 'h.mp4' in str(item).lower():
                    mkitem['VideoHref'] = item
        except:
            mkitem['VideoHref'] = ''
        yield mkitem
