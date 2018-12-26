import json
import queue
from tools.push_tools import PushTool
import requests
import sys
from configparser import ConfigParser
from datetime import datetime
import time

success_count = 0
failure_count = 0
start_time = datetime.now()
cookie = PushTool.get_cookies()
config = ConfigParser()
config.read('config.ini', 'utf-8')
target = config.get('bd_push', 'target')


_COOKIE_FILE = "mylibs/cookie.txt"
_COOKIE_FILE_INVALID = "mylibs/cookie-invalid.txt"
_COOKIE_EXPIRE_COUNT = 10
_THREAD_SIZE = 2


class BaiduSubmit:
    def __init__(self):
        self._refill_cookies()
        self._change_cookie()
        self._url_buffer = queue.Queue()

    def _refill_cookies(self):
        all_cookies = [line.strip() for line in open(_COOKIE_FILE, encoding="UTF-8")]
        invalid_cookies = set([line.strip() for line in open(_COOKIE_FILE_INVALID, encoding="UTF-8")])
        self._cookies = list(filter(lambda cookie: cookie not in invalid_cookies, all_cookies))

    def _drop_cookie(self):
        with open(_COOKIE_FILE_INVALID, mode="a", encoding="UTF-8") as f:
            f.write(self._cookie + "\n")

    def _change_cookie(self):
        if not self._cookies:
            self._refill_cookies()
        self._cookie = self._cookies.pop()
        print("change cookie")

    def submit(self, num):
        global target
        global failure_count
        global success_count
        while True:

            url = ''
            code = 233
            try:
                url = PushTool.rand_all(target)
                resp, url = self._do_submit(url)
                code = resp.status_code
                if code != 200:
                    failure_count += 1
                    self._change_cookie()
                    print('返回代码异常')
                else:
                    resp_entity = json.loads(resp.text)
                    if "status" not in resp_entity or resp_entity["status"] != 0:
                        failure_count += 1
                        self._drop_cookie()
                        self._change_cookie()
                        print(resp_entity)
                    else:
                        print('成功！')
                        success_count += 1
            except Exception as e:
                print(e)
                failure_count += 1
                print('服务器异常')
                time.sleep(3)
            # this_time = datetime.now()
            # spend = this_time - start_time
            # if int(spend.seconds) == 0:
            #     speed_sec = success_count / 1
            # else:
            #     speed_sec = success_count / int(spend.seconds)
            # speed_day = float('%.2f' % ((speed_sec * 60 * 60 * 24) / 10000000))
            # percent = success_count / (failure_count + success_count) * 100
            # sys.stdout.write(' ' * 100 + '\r')
            # sys.stdout.flush()
            # print(url)
            # sys.stdout.write('%s 成功%s 预计(day/千万):%s M 成功率:%.2f%% 状态码:%s\r' % (datetime.now(), success_count, speed_day, percent, code))
            # sys.stdout.flush()

    def _do_submit(self, url):
        url = url.strip()
        headers = {"Connection": "keep-alive",
                   "Origin": "https://ziyuan.baidu.com",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "Accept": "application/json, text/javascript, */*; q=0.01",
                   "X-Requested-With": "XMLHttpRequest",
                   "X-Request-By": "baidu.ajax",
                   "Referer": "https://ziyuan.baidu.com/linksubmit/url",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,mr;q=0.6",
                   "Cookie": self._cookie,
                   }
        resp = requests.post(url="https://ziyuan.baidu.com/linksubmit/urlsubmit",
                             data={"url": url},
                             headers=headers,
                             # proxies=self._proxy,
                             timeout=10)
        return resp, url