import requests
from bs4 import BeautifulSoup
import pymongo

# response = requests.get('https://read.jd.com/6744/').content

# soup = BeautifulSoup(response, 'lxml')

# a = soup.findAll('a', attrs={'title':'目录'})
# for i in a:
#     print(i.text.strip())
mongo = pymongo.MongoClient('127.0.0.1', 27017)

def find_bookstores():
    bookstores = mongo.jdread.bookstores.find()

    num = 0
    su_m = 0
    for i in bookstores:
        for b in i['bookstore']:
            print('=====================')
            print(b['book_name']+"----"+b['book_href'])
            print('=====================')
            su_m+=1
            for c in  b['book_chapters']:
                print(c['chapter_name']+"----"+c['chapter_url'])
                num += 1
    print(su_m)
    print(num)
    print(bookstores.count())

def find_books():
    books = mongo.jdread.books.find()
    num = 0
    for b in books:
        # for c in b['booK_chapters']:
        #     print(c['title'])
        print(b['book_name'])
        num+=1
    print(num)

find_bookstores()
# find_books()