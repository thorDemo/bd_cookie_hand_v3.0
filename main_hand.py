from threadpool import ThreadPool, makeRequests
from configparser import ConfigParser
from mylibs.new_submit import BaiduSubmit


config = ConfigParser()
config.read('config.ini', 'utf-8')
thread_num = int(config.get('bd_push', 'thread'))
cookie_file = config.get('bd_push', 'cookie_file')
pool = ThreadPool(thread_num)
arg = []
cookie = open(cookie_file, 'r+', encoding='UTF-8')
for x in cookie:
    arg.append(x.strip())
Sub = BaiduSubmit()
request = makeRequests(Sub.submit, arg)
[pool.putRequest(req) for req in request]
pool.wait()
