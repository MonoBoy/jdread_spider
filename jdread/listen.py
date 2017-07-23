import pymongo

mongo = pymongo.MongoClient('127.0.0.1', 27017)
bookclasses = mongo.jdread.bookclasses.find()
# for i in bookclasses:
#    for c in i['book_classes']:
#        print(c['book_class'],c['book_href'])

bookstores = mongo.jdread.bookstores.find()
for b in bookstores:
    print(b['name'])
    for s in b['bookstore']:
        print(s['book_name'])
#books = mongo.jdread.books.find()
#print(books.count())