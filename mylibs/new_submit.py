import json
import queue
from tools.push_tools import PushTool
import requests
import sys
from configparser import ConfigParser
from datetime import datetime
import time
import traceback

config = ConfigParser()
config.read('config.ini', 'utf-8')
success_count = 0
failure_count = 0
start_time = datetime.now()
_COOKIE_EXPIRE_COUNT = 10
target = config.get('bd_push', 'target')


class BaiduSubmit:
    def submit(self, _cookies):
        global target
        global failure_count
        global success_count
        expire_count = _COOKIE_EXPIRE_COUNT
        while expire_count > 0:
            url = ''
            code = 233
            try:
                url = PushTool.rand_all(target)
                resp, url = self._do_submit(url, _cookies)
                code = resp.status_code
                if code != 200:
                    failure_count += 1
                else:
                    resp_entity = json.loads(resp.text)
                    if "status" not in resp_entity or resp_entity["status"] != 0:
                        failure_count += 1
                    else:
                        success_count += 1
                    expire_count -= 1
            except Exception as e:
                traceback.print_exc(E)
                failure_count += 1
                print('服务器异常')
                time.sleep(3)
            this_time = datetime.now()
            spend = this_time - start_time
            if int(spend.seconds) == 0:
                speed_sec = success_count / 1
            else:
                speed_sec = success_count / int(spend.seconds)
            speed_day = float('%.2f' % ((speed_sec * 60 * 60 * 24) / 10000000))
            percent = success_count / (failure_count + success_count) * 100
            sys.stdout.write(' ' * 100 + '\r')
            sys.stdout.flush()
            print(url)
            sys.stdout.write(
                '%s 成功%s 预计(day/千万):%s M 成功率:%.2f%% 状态码:%s\r' %
                (datetime.now(), success_count, speed_day, percent, code))
            sys.stdout.flush()

    def _do_submit(self, url, _cookie):
        url = url.strip()
        headers = {"Connection": "keep-alive",
                   "Origin": "https://ziyuan.baidu.com",
                   "User-Agent": PushTool.user_agent(),
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "Accept": "application/json, text/javascript, */*; q=0.01",
                   "X-Requested-With": "XMLHttpRequest",
                   "X-Request-By": "baidu.ajax",
                   "Referer": "https://ziyuan.baidu.com/linksubmit/url",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,mr;q=0.6",
                   "Cookie": _cookie,
                   }
        resp = requests.post(url="https://ziyuan.baidu.com/linksubmit/urlsubmit",
                             data={"url": url},
                             headers=headers,
                             # proxies=self._proxy,
                             timeout=10)
        return resp, url
