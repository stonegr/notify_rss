"""
这个类用来解析xml，动态获取所需要的字段

接受以下格式
all_config=总的配置文件
indata=spider类返回的对应二进制数据

对spider的空数据也处理为空数据

返回:
{
    'name':{
        'mainkey':{
            'key':'value'
        }
    }
}
"""

import feedparser
from bs4 import BeautifulSoup
import json

from base.base import *

from common.config_do import Config_do

# 传入parser和需要获取的类型，int获得相应的值(未用)
def get_item_l(parser_i, type: str, num: int = None):
    _data = []
    for i in parser_i[:num]:
        if type == "text":
            _data.append(i.get_text(strip=True))
        else:
            _data.append(i.attrs.get(type))
    return _data


class Parser:
    """
    :param allconfig,总的配置文件
    :param indata,{'name':'二进制数据'}
    """

    def __init__(self):
        self.data = {}

    def go_Parser_xml(self, allconfig, indata):
        self.__get_keys(allconfig)
        self.indata = indata
        for i, d in self.indata.items():
            self.__parser(
                i,
                d,
                self.keys.get(i).get("keys"),
                self.keys.get(i).get("type"),
                Config_do.get_self(
                    allconfig,
                    ["data", i, "mainkey"],
                    list_dict_keys(self.keys.get(i).get("keys"))[0],
                ),
            )

    def __parser(self, name: str, data: dict, keys: dict, type: str, mainkey: str):
        _data = {}
        if type == "rss":
            f = feedparser.parse(data)
            for i in f.entries:
                _data_tmp = {}
                for i_ in keys:
                    _data_tmp[i_] = i.get(i_)
                _data[_data_tmp[mainkey]] = _data_tmp
        elif type == "json":
            _data_tmp = {}
            d_ = json.loads(data)
            for item in d_.select(Config_do.config["data"][name]["main_list"]):
                _data_tmp = {}
                for i, d in keys.items():
                    _data_tmp[i] = (
                        item.get(d.get("path")).strip()
                        if item.get(d.get("path"))
                        else item.get(d.get("path"), "None")
                    )
                if d.get("start"):
                    _data_tmp[i] = d.get("start") + _data_tmp[i]
                _data[_data_tmp[mainkey]] = _data_tmp
        elif type == "html":
            d_ = BeautifulSoup(data, "lxml")
            for item in d_.select(Config_do.config["data"][name]["main_list"]):
                _data_tmp = {}
                for i, d in keys.items():
                    if d.get("type", "text") == "text":
                        _data_tmp[i] = item.select(d.get("path"))[
                            d.get("index", 0)
                        ].get_text(strip=True)
                    else:
                        _data_tmp[i] = item.select(d.get("path"))[
                            d.get("index", 0)
                        ].attrs.get(d.get("type", "None"))
                    if d.get("start"):
                        _data_tmp[i] = d.get("start") + _data_tmp[i]
                _data[_data_tmp[mainkey]] = _data_tmp

        self.data[name] = _data

    def __get_keys(self, allconfig: dict):
        """
        这个类用来获取需要的title
        返回值是["title", "link"]
        """
        keys = {}
        for i, d in allconfig.get("data").items():
            keys[i] = {}
            if d.get("keys") and d.get("type"):
                keys[i]["keys"] = d.get("keys")
                keys[i]["type"] = d.get("type")
            else:
                keys[i]["keys"] = ["title", "link"]
                keys[i]["type"] = "rss"

        self.keys = keys
