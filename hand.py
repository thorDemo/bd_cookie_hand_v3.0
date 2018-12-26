from threadpool import ThreadPool, makeRequests
from configparser import ConfigParser
from mylibs.hand_with_cookie import BaiduSubmit
import datetime
import time


def main():
    while True:
        today = datetime.datetime.now().strftime('%Y%m%d')
        print('to do %s' % today)
        config = ConfigParser()
        config.read('config.ini', 'utf-8')
        thread_num = int(config.get('bd_push', 'thread'))
        target = config.get('bd_push', 'target')
        pool = ThreadPool(thread_num)
        arg = []
        for x in range(0, thread_num):
            arg.append(target)
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