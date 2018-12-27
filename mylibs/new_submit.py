import json
import queue
from tools.push_tools import PushTool
import requests
import sys
from configparser import ConfigParser
from datetime import datetime
import time
import traceback
from requests.exceptions import ReadTimeout, ConnectionError

config = ConfigParser()
config.read('config.ini', 'utf-8')
success_count = 0
failure_count = 0
start_time = datetime.now()
_COOKIE_EXPIRE_COUNT = 10
target = config.get('bd_push', 'target')


class BaiduSubmit:
    def my_proxy(self):
        proxy = requests.get("http://127.0.0.1:5010/get/").content
        return proxy

    def submit(self, _cookies):
        global target
        global failure_count
        global success_count
        expire_count = _COOKIE_EXPIRE_COUNT
        while expire_count > 0:
            expire_count -= 1
            url = ''
            code = 233
            status = 1
            cookie = ''
            try:
                url = PushTool.rand_all(target)
                resp, url, cookie = self._do_submit(url, _cookies)
                code = resp.status_code
                if code != 200:
                    failure_count += 1
                else:
                    resp_entity = json.loads(resp.text)
                    if "status" not in resp_entity or resp_entity["status"] != 0:
                        status = resp_entity["status"]
                        failure_count += 1
                    else:
                        success_count += 1
            except Exception as e:
                # traceback.print_exc(e)
                failure_count += 1
                # print('服务器异常')
                # time.sleep(3)
            percent = success_count / (failure_count + success_count) * 100
            sys.stdout.write(' ' * 100 + '\r')
            sys.stdout.flush()
            print(status, code, url, _cookies)
            sys.stdout.write(
                '%s 成功%s 失败%s 成功率:%.2f%% 状态码:%s 返回值: %s \r' %
                (datetime.now(), success_count, failure_count, percent, code, status))
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
        try:
            # proxy = {'http': 'http://60.217.153.75:8060'}
            # try:
            #     proxy['http'] = 'http://%s' % str(self.my_proxy(), encoding='utf-8').strip('')
            # except:
            #     print('\033[31;1m本地链接超时 重试！！！！！！')
            resp = requests.post(url="https://ziyuan.baidu.com/linksubmit/urlsubmit",
                                 data={"url": url},
                                 headers=headers,
                                 # proxies=proxy,
                                 timeout=1)
        except (ReadTimeout, ConnectionError):
            print('超时')
            return
        return resp, url, headers['Cookie']
