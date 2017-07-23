# coding:utf-8
import requests
import time
import re
import pymongo
from lxml.html import etree
from bs4 import BeautifulSoup

from logutils import Logger
from common import mongo, headers


class AiduSpider():
    def __init__(self):
        self.name = "aidu"
        self.domain = 'https://read.jd.com/'
        self.book_classes_url = '{0}?sm.pageSize=20&sm.sortField=1&sm.keyType=1&page={1}'
        self.logger = Logger('jdread', 'jdread.log').get_logger()
        self.jd_bookclasses = mongo.jdread.bookclasses
        self.jd_bookstores = mongo.jdread.bookstores
        self.jd_books = mongo.jdread.books
        self.jd_errors = mongo.jdread.errors
        self.jd_retry = mongo.jdread.retry


    def crawl_page_source(self, url):
        try:
            response = requests.get(url, headers=headers).text
        except requests.ConnectionError as e:
            self.logger.error("url：%s请求错误%s" % (url, e))
            self.jd_retry.insert({'type': 'connection', 'url': url, 'time': time.ctime()})
        return response


    def get_classify(self):
        url = self.domain
        href = ''
        name = ''
        try:
            response  = self.crawl_page_source(url)

            # 一级分类及其一级分类下的二级分类
            # 二级分类下的novel的名字和链接
            # print(result)
            selector = etree.HTML(response)
            dt = selector.xpath('//*[contains(@class, "novels novels-")]/dt')
            for i in range(0, len(dt)):
                classify_name = dt[i].text
                print(classify_name)
                book_href = selector.xpath('//*[@id="sort-list"]/dl[contains(@class,"novels novels-")]['+str(i+1)+']/dd/a')
                book_classes = []
                for j in range(0, len(book_href)):
                    href = 'https:'+book_href[j].get('href')
                    name = book_href[j].text
                    self.crawl_classes_books(name, href)
                    book_classes.append({'book_class': name, 'book_href': href})
                data = {
                    'classify_name': classify_name,
                    'book_classes': book_classes
                }
                print(data)
                #self.jd_bookclasses.insert(data)
        except Exception as e:
            self.logger.error("出现%s错误，name是% shref是%s"%(e, name, href))
            error = {
                'time': time.ctime(),
                'error_msg': e,
                'error_href': href,
                'error_name': name
            }
            self.jd_errors.insert(error)


    # 爬取每个分类下的书籍
    def crawl_classes_books(self, name='', url=''):
        for i in range(150):
            page_url = self.book_classes_url.format(url, i+1)
            print(page_url)
            response = self.crawl_page_source(page_url)
            if self.page_istrue(response):
                selector = etree.HTML(response)

                book_urls = selector.xpath('//*[@class="w clearfix"]//a[@class="link630"]')
                bookstores = []
                for index in range(0,len(book_urls)):
                    book_href = 'https:'+book_urls[index].get('href').strip()
                    # 获取每部书籍的章节
                    book_chapters = self.crawl_book_chapters(book_href)
                    bookstores.append({'book_name': book_urls[index].text, 'book_href': book_href, 'book_chapters': book_chapters})
                data = {
                    'source_page_url': page_url,
                    'name': name,
                    'bookstore': bookstores
                }
                print(data)
                #self.jd_bookstores.insert(data)
            else:
                self.logger.error('this %s url was requests error' % page_url)
                #self.jd_retry.insert({'type': 'data of page is none', 'url': page_url, 'time': time.ctime()})
                break


    # 爬取每本书籍的简介，章节名字和链接
    def crawl_book_chapters(self, url):
        response = self.crawl_page_source(url)
        soup = BeautifulSoup(response, 'lxml')
        # 书籍简介
        bookintro = soup.find('div', attrs={'id': 'box-bookintro-mirror'}).text
        # print(bookintro)
        # 出版信息等
        book_authorinfo = soup.find('div', attrs={'class': 'book-authorinfo'}).text.strip()
        # print(book_authorinfo)
        chapter_list = soup.findAll('a', attrs={"href": re.compile(r'^\/\/read.jd.*\/\d+\/\d+.html$')})
        # print(chapter_list)
        bookdetail = []
        for a in chapter_list:
            bookdetail.append({'bookintro': bookintro, 'book_authorinfo': book_authorinfo.encode('utf-8').decode('utf-8'), 'chapter_name': a.text.strip(), 'chapter_url': 'https:'+a.get('href')})
            #print(a.text+'--'+a.get('href'))
        # print(bookdetail)
        return bookdetail # 返回每部书籍的所有章节

    # 爬取文章每个章节的内容
    def crawl_chapter_words(self, chapter_url):
        response = self.crawl_page_source(chapter_url)
        soup = BeautifulSoup(response, 'lxml')
        chapter_div = soup.find('div', attrs={'class': 'mc clearfix'})
        title = chapter_div.h1.text
        content = ''
        for p in chapter_div.findAll('p'):
            # print(p.text)
            content = content + p.text+'\n'
        result = {'title': title, 'chapter_content': content}
        print(result)
        return result

    def crawl_per_book(self):
        bookstores = self.jd_bookstores.find().skip(100).limit(100)
        num = 0
        try:
            for bookstore in bookstores:
                # downed = ["情感婚恋", "校园生活", "职场社会", "官场商战", "都市乡土", "网络魔幻"]
                downed = []
                # book 是每一本书
                if bookstore['name'] not in downed:
                    for book in bookstore['bookstore']:
                        chapters = []  # 每部书籍的所有章节内容
                        for book_chapter in book['book_chapters']:
                            chapter_url = book_chapter['chapter_url']
                            if chapter_url.startswith('https://read.jd.com'):
                                # print(chapter_url)
                                result = self.crawl_chapter_words(chapter_url)
                                chapters.append(result)
                                time.sleep(0.5)
                        num = num + 1
                        data = {
                            'book_href': book['book_href'],
                            'book_name': book['book_name'],
                            'booK_chapters': chapters
                        }
                        #self.jd_books.insert(data)
                        self.logger.info('<%s>类中的第%s部书籍《%s》读取成功' % (bookstore['name'], num, book['book_name']))
                    self.logger.info("%s分类书籍完成" % bookstore['name'])
                    downed.append(bookstore['name'])
        except Exception as err:
            self.logger.error(err)
        except pymongo.errors.CursorNotFound as e:
            self.logger.error(e)
            #self.jd_errors.insert({'error_msg': e, 'time': time.ctime()})

    def page_istrue(self, response):
        selector = etree.HTML(response)
        if selector.xpath('//div[@class="list3 clearfix"]'):
            return True
        else:
            return False


if __name__ == '__main__':
    spider = AiduSpider()
    # response = requests.get('http://www.woaidu.org/sitemap_1.html')
    # result = response.content
    # print(spider.parse(result))
    # response = requests.get('https://read.jd.com/')
    # result = response.content.decode('utf-8')
    # spider.parse_detail(result)
    # spider.get_classify()
    # spider.crawl_classes_books(url='https://read.jd.com/list/1-t14.html')
    # spider.crawl_book_words('https://read.jd.com/15273/')
    # spider.crawl_book_chapters('https://read.jd.com/6744/')
    # spider.crawl_chapter_words('https://read.jd.com/6744/342971.html')
    spider.crawl_per_book()

