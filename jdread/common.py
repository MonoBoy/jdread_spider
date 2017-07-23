import pymongo

mongo = pymongo.MongoClient('127.0.0.1', 27017)

user_agent = []

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': '3AB9D23F7A4B3C9B=NCUT4XA2OSUKQNKE2GOJJJ5RK3CHIFKIKXCHJU2MY7WL3NOQOHDQV2YZINZUCK3BKIE6LTRWVLH3S7TW2IQVYL5ZMU',
    'Host': 'read.jd.com',
    'Referer': 'https://read.jd.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}