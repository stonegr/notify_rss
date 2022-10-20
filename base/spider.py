"""
这个类用来对url列表异步请求，获取二进制数据

接受下列格式

        "n0": {
            "url": "url...", # 必填
            "kws": {
                "proxy": true
            },
            "cron": "* * * * *",
            "keys": [
                "title",
                "link"
            ]
        },
        "n1": {
            "url": "url...",
            "kws": {
                "proxy": true
            },
            "cron": "* * * * *",
            "keys": [
                "title",
                "link",
                "published"
            ]
        },

"""

import aiohttp
import asyncio
from functools import wraps


def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise

    return wrapper


# 去除time_error
from asyncio.proactor_events import _ProactorBasePipeTransport

_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(
    _ProactorBasePipeTransport.__del__
)

from .logging_ import logger


class Spider_Aio:
    """
    :param config,配置文件示例
    {
    "p3terx": {
        "type": "rss",
        "enable": True,
        "url": "https://p3terx.com/feed/",
        "kws": {"proxy": True, "timeout": 10},
        "cron": "0/30 0,6-23 * * *",
        "mainkey": "link",
        }
    }
    :param indata,{'name':'二进制数据'}
    """

    def __init__(self):
        self.htmls = {}

    def go_Spider_Aio(self, config, sem=10):
        self.config = config
        self.sem = sem
        self.__main(self.config)

    async def aio_request(
        self,
        url,
        lx="get",
        proxy=None,
        headers={},
        cookies="",
        json="",
        timeout=5,
    ):
        """
        异步请求
        """

        headers0 = {
            # "Connection": "keep-alive",
            "Connection": "close",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,la;q=0.6",
            "cookie": cookies,
        }

        if cookies == "":
            headers0.pop("cookie")

        if headers == {}:
            headers = headers0

        proxies = f"http://{proxy}"

        kw_all = dict(
            proxy=proxies,
            headers=headers,
            cookies=cookies,
            timeout=aiohttp.ClientTimeout(total=timeout),
            json=json,
        )

        if not proxy:
            kw_all.pop("proxy")

        if lx != "post":
            kw_all.pop("json")
            kw_all.pop("cookies")

        async with asyncio.Semaphore(self.sem):
            try:
                async with aiohttp.ClientSession() as session:  # 获取session
                    async with session.request(
                        lx, url.split(",")[1], **kw_all
                    ) as resp:  # 提出请求

                        # html_unicode = await resp.text()
                        # html = bytes(bytearray(html_unicode, encoding='utf-8'))

                        html = await resp.read()  # 可直接获取bytes
                        # html = await resp.text()  # 可直接获取bytes
                        # print(html)
                        # return html
                        logger.info(f'{url.split(",")[0]} fetch success')
                        self.htmls[url.split(",")[0]] = html
            except:
                # traceback.print_exc()
                # logger.error(
                #     f'{url.split(",")[0]} is null,please check!', exc_info=True
                # )
                logger.error(f'{url.split(",")[0]} is null,please check!')
                self.htmls[url.split(",")[0]] = ""

    def __main(self, config):
        # loop = asyncio.get_event_loop()  # 获取事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = []
        for i, d in config.items():
            if d.get("kws"):
                tasks.append(self.aio_request(i + "," + d.get("url"), **d.get("kws")))
            else:
                tasks.append(self.aio_request(i + "," + d.get("url")))
        loop.run_until_complete(asyncio.wait(tasks))  # 激活协程
        loop.close()
