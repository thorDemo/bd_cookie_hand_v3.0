import json
import queue
import threading
import requests
from tools.push_tools import PushTool

_COOKIE_FILE = "mylibs/hedy_cookie.txt"
_COOKIE_FILE_INVALID = "mylibs/cookie-invalid.txt"
_COOKIE_EXPIRE_COUNT = 10
_THREAD_SIZE = 2
# _PROXY_CONF = json.load(open(app_env.get_app_root() + "/baidu_submit/proxy.json", encoding="UTF-8"))


class BaiduSubmit:
    def __init__(self):
        self._refill_cookies()
        self._change_cookie()
        self._url_buffer = queue.Queue()
        self.start_buffer_consumer()

    def _refill_cookies(self):
        all_cookies = [line.strip() for line in open(_COOKIE_FILE, encoding="UTF-8")]
        invalid_cookies = set([line.strip() for line in open(_COOKIE_FILE_INVALID, encoding="UTF-8")])
        self._cookies = list(filter(lambda cookie: cookie not in invalid_cookies, all_cookies))

    # def _change_proxy(self):
    #     while True:
    #         proxy_resp = requests.get(
    #             _PROXY_REPO.format(_PROXY_CONF["spiderId"], _PROXY_CONF["orderNo"]))
    #         print("got next proxy: " + proxy_resp.text)
    #         proxy = json.loads(proxy_resp.text)["RESULT"][0]
    #         proxy = {"http": proxy["ip"] + ":" + proxy["port"], "https": proxy["ip"] + ":" + proxy["port"]}
    #         try:
    #             resp = requests.get(url="https://m.baidu.com", timeout=10, proxies=proxy)
    #             resp.encoding = "UTF-8"
    #             if resp.text.find("百度") > 0:
    #                 self._proxy = proxy
    #                 print("change proxy.")
    #                 break
    #         except Exception as e:
    #             pass
    #         print("proxy not available, try next")
    #         time.sleep(5)

    def _drop_cookie(self):
        with open(_COOKIE_FILE_INVALID, mode="a", encoding="UTF-8") as f:
            f.write(self._cookie + "\n")

    def _change_cookie(self):
        if not self._cookies:
            self._refill_cookies()
        self._cookie = self._cookies.pop()
        print("change cookie.")

    def start_buffer_consumer(self):
        threading.Thread(target=self._consume_buffer)

    def _consume_buffer(self):
        while True:
            self.submit(self._url_buffer.get().url)

    def submit(self, url):
        retry_times = 0
        while True:
            try:
                resp, url = self._do_submit(url)
                if resp.status_code != 200:
                    print("[retry {}]post error with code: {}".format(retry_times, resp.status_code))
                    retry_times += 1
                    self._change_cookie()
                else:
                    resp_entity = json.loads(resp.text)
                    if "status" not in resp_entity or resp_entity["status"] != 0:
                        print("[retry {}]post error with response: {}".format(retry_times, resp.text))
                        retry_times += 1
                        self._drop_cookie()
                        self._change_cookie()
                    else:
                        # UrlLogger.get_instance("success").info(url)
                        print(resp.text)
                        print("url " + url + " done.")
                        return True
            except Exception as e:
                print("[retry {}]post error with exception: {}".format(retry_times, repr(e)))
                retry_times += 1
                # self._change_proxy()

            if retry_times >= 3:
                # UrlLogger.get_instance("failed").info(url)
                print("post error due to cookie and proxy both has been changed for limit times.")
                return False

    def _do_submit(self, url):
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
                   "Cookie": self._cookie,
                   }
        resp = requests.post(url="https://ziyuan.baidu.com/linksubmit/urlsubmit",
                             data={"url": url},
                             headers=headers,
                             timeout=10)
        return resp, url


