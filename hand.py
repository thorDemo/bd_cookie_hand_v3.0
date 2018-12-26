from threadpool import ThreadPool, makeRequests
from configparser import ConfigParser
from mylibs.hand_with_cookie import BaiduSubmit


config = ConfigParser()
config.read('config.ini', 'utf-8')
thread_num = int(config.get('bd_push', 'thread'))
target = config.get('bd_push', 'target')
pool = ThreadPool(thread_num)
arg = []
for x in range(0, thread_num):
    arg.append(target)
Sub = BaiduSubmit()
request = makeRequests(Sub.submit, arg)
[pool.putRequest(req) for req in request]
pool.wait()
