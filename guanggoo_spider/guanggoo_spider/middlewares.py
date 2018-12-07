# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random

from scrapy import signals
from scrapy.conf import settings
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from .user_agents import agents
from selenium import webdriver
from scrapy.http import HtmlResponse
from pydispatch import dispatcher


class GuanggooSpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GuanggooSpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        # 这句话用于随机选择user-agent
        # print("agents type: {0}, length: {1}".format(type(agents), len(agents)))
        # print("agents: " + "|".join(agents))
        ua = random.choice(agents)
        print("select user agent: " + ua)
        if ua:
            request.headers.setdefault('User-Agent', ua)

    # the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    # user_agent_list = [
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    #     "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    #     "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    #     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    #     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    #     "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    #     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    #     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    #     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    # ]


class JavaScriptMiddleware(object):
    def __init__(self):
        if settings['LOGIN_TYPE'] == 'MyCrawl':
            '''
            self.simulation = weibo_login(settings['USERNAME'], settings['PWD'], 
            settings['COOKIE_FILE'])
            cookie_file = settings['COOKIE_FILE']
            cookie_jar = cookielib.LWPCookieJar(cookie_file)
            cookie_jar.load(ignore_discard=True, ignore_expires=True)
            self.driver = webdriver.PhantomJS(executable_path=settings['JS_BIN'])
            for c in cookie_jar:
                self.driver.add_cookie({'name': c.name, 'value': c.value, 'path': '/', 'domain': c.domain})
            '''
            #  simulate user login process
            self.driver = webdriver.PhantomJS(executable_path=settings['JS_BIN'])
            #             登录
            #             self.driver.get('http://login.sina.com.cn/')
            #             uid = self.driver.find_element_by_id('username')
            #             upw = self.driver.find_element_by_id('password')
            #             loginBtn = self.driver.find_element_by_class_name('smb_btn')
            #             time.sleep(1)
            #             uid.send_keys(settings['USERNAME'])
            #             upw.send_keys(settings['PWD'])
            #             loginBtn.click()
            #             time.sleep(1)
        elif settings['LOGIN_TYPE'] == 'other':
            print('add login code')
            pass
        else:
            self.driver = webdriver.PhantomJS(executable_path=settings['JS_BIN'])
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def process_request(self, request, spider ):
        self.driver.get(request.url)
        # spider.logger.info("页面渲染中····开始自动下拉页面")
        # indexPage = 1000
        # height = self.driver.execute_script("return document.body.offsetHeight")
        # spider.logger.info("height for page %s is %d" % (request.url, height))
        # while indexPage < height:
        #     self.driver.execute_script("scroll(0," + str(indexPage) + ")")
        #     indexPage = indexPage + 1000
        #     # print(indexPage)
        #     time.sleep(0.5)

        spider.logger.info("process page %s finished" % request.url)
        rendered_body = self.driver.page_source
        # 编码处理
        if r'charset="GBK"' in rendered_body or r'charset=gbk' in rendered_body:
            coding = 'gbk'
        else:
            coding = 'utf-8'
        return HtmlResponse(request.url, body=rendered_body, encoding='utf-8')
        # 关闭浏览器

    def spider_closed( self, spider, reason ):
        print ('close driver......')
        self.driver.close()