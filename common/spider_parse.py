from base.spider import Spider_Aio
from base.parser import Parser

from base.logging_ import *


class Spider_parser(Spider_Aio, Parser):
    """
    :param allconfig,总的配置文件
    :param indata,{'name':'二进制数据'}
    :param do_data,总配置文件的data段,传入示例
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
    """

    def __init__(self, allconfig: dict, sem, do_data: dict):
        Spider_Aio.__init__(self)
        Parser.__init__(self)
        self.allconfig = allconfig
        self.sem = sem
        self.do_data = do_data

    def go_Spider_parser(self):
        self.__get_content()
        self.__parse_content()
        return self.data

    def __get_content(self):
        self.go_Spider_Aio(self.do_data, self.sem)

    def __parse_content(self):
        self.go_Parser_xml(
            self.allconfig,
            self.htmls,
        )
