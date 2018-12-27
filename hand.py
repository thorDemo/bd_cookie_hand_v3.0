from threadpool import ThreadPool, makeRequests
from configparser import ConfigParser
# from mylibs.hand_with_cookie import BaiduSubmit
from mylibs.new_submit import BaiduSubmit
import datetime
import time


def main():
    while True:
        today = datetime.datetime.now().strftime('%Y%m%d')
        print('to do %s' % today)
        config = ConfigParser()
        config.read('config.ini', 'utf-8')
        thread_num = int(config.get('bd_push', 'thread'))
        cookie_file = config.get('bd_push', 'cookie_file')
        pool = ThreadPool(thread_num)
        arg = []
        cookie = open(cookie_file, 'r+', encoding='UTF-8')
        for x in cookie:
            arg.append(x.strip())
        sub = BaiduSubmit()
        request = makeRequests(sub.submit, arg)
        [pool.putRequest(req) for req in request]
        pool.wait()
        while True:
            time.sleep(1)
            tomorrow = datetime.datetime.now().strftime('%Y%m%d')
            if today != tomorrow:
                break


if __name__ == '__main__':
    main()