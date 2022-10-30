import abc
import time
import json
import re
import ast


class controller_metaclass(abc.ABC):
    @abc.abstractmethod
    def _get(self):
        pass

    @abc.abstractmethod
    def _insert(self):
        pass


from common.models.url_data import UrlDatum
from common.models.user_log import UserLog

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# notify
from notify.wechat import Wechat
from notify.telegram_ import Telegram
from common.config_do import Config_do
from base.do_sql import *

# engine = create_engine("sqlite:///static/db/rss.db", echo=False)
# Session = sessionmaker(bind=engine)


def list_content(data: str) -> dict:
    """
    这个方法用来处理从数据库拿来的contents,恢复为dict
    """
    if data:
        # _data = list(map(json.loads, re.findall("{.*?}", data)))
        # _data = json.loads(re.sub("(['])", '"', data))
        try:
            _data = ast.literal_eval(data)
        except:
            _data = {}
        if not isinstance(_data, dict):
            _data = {}
    else:
        _data = {}
    return _data


def compare_dict(new_dict: dict, old_dict: dict, today_dict: dict):
    """
    这个函数用来比较初始dict和原dict之间的差别，并且返回初始dict-原始dict的值，若没有则返回空dict
    """
    _data = {}
    for i in new_dict:
        if (i not in old_dict) and (i not in today_dict):
            _data[i] = new_dict.get(i)
    return _data


def add_current_contents(today_contents: str, change_contetns: dict):
    """
    这个函数用来将新增的数据添加到已有的today_contents中
    """
    try:
        today_contents = ast.literal_eval(today_contents)
    except:
        today_contents = {}
    if not isinstance(today_contents, dict):
        today_contents = {}
    for i, d in change_contetns.items():
        if i not in today_contents:
            today_contents[str(i)] = d
    return str(today_contents)


def check_status_task(data: dict, moudle):
    """
    数据库(data)的预处理
    """
    session = Session()
    for i, d in data.items():
        if i == "enable":
            # 今天之前的enable设置为1,need_update设置为0
            session.execute(
                "UPDATE url_data SET enable=1,need_update=0 WHERE date < date('now','localtime') and name {}".format(
                    sql_tuple(d)
                )
            )
            # 今天的enable设置为1,need_update设置为1
            session.execute(
                "UPDATE url_data SET enable=1,need_update=1 WHERE date = date('now','localtime') and name {}".format(
                    sql_tuple(d)
                )
            )
        elif i == "disable":
            # 今天和今天之前的enable设置为0,need_update设置为0
            session.execute(
                "UPDATE url_data SET enable=0,need_update=0 WHERE date <= date('now','localtime') and name {}".format(
                    sql_tuple(d)
                )
            )
        session.commit()
        session.close()


def check_status_user(data: dict, moudle):
    """
    数据库(user)的预处理

    :param data:user的dict,示例
    {'enable': ['stone', 'stone2'], 'disable': []}
    """
    session = Session()
    for i, d in data.items():
        if i == "enable":
            for i_ in d:
                # 检测是否有这个user的数据，没有就创建
                _user_m = session.query(UserLog).filter(UserLog.name == i_).all()
                if not _user_m:
                    session2 = Session()
                    session2.add(UserLog(name=i_))
                    session2.commit()
                    session2.close()

            # 将现在现有的进行初始化处理
            session.execute(
                "UPDATE user_log SET enable=1 WHERE name {}".format(
                    sql_tuple(d),
                )
            )
        elif i == "disable":
            # 今天和今天之前的enable设置为0,need_update设置为0
            session.execute(
                "UPDATE user_log SET enable=0,current_contents='' WHERE name {}".format(
                    sql_tuple(d)
                )
            )
        session.commit()
        session.close()


def notify(notify_contents: dict, title, _notify_cate: dict = {}):
    """
    发送通知的总封装

    :param notify_content,单个/多个通知,{'name':{}}
    :param _notify_cate,可以指定发送方式
    :pram title,发送的消息title,url_title,user_title
    """
    if not _notify_cate:
        _notify_cate = Config_do.get_self(
            Config_do.config,
            ["data", list(notify_contents.keys())[0], "methods"],
            Config_do.get_self(Config_do.config, ["config", "methods"]),
        )  # 获取需要通知的方式
    for i_, d_ in _notify_cate.items():
        if i_ == "wechat":
            Wechat(
                Config_do.get_self(Config_do.config, ["tz", "wechat", "wecom_aid"]),
                Config_do.get_self(Config_do.config, ["tz", "wechat", "wecom_cid"]),
                Config_do.get_self(Config_do.config, ["tz", "wechat", "wecom_secret"]),
            ).fs(
                notify_contents,
                d_.get("wecom_uid"),
                Config_do.get_self(Config_do.config, ["config", title], "有新的订阅更新啦"),
            )
        elif i_ == "telegram":
            Telegram(
                Config_do.get_self(Config_do.config, ["tz", "telegram", "token"]),
            ).fs(
                notify_contents,
                d_.get("chat_id"),
                Config_do.get_self(Config_do.config, ["config", title], "订阅汇总来啦"),
            )


# 获取时间
def get_time(format="%Y-%m-%d"):
    """
    %Y-%m-%d %H:%M:%S
    """

    return time.strftime(format, time.localtime())


# 执行数据库的tuple处理，单个时，报错
def sql_tuple(d: list):
    """
    :param l,表中name的list
    """
    if len(d) == 1:
        return "=" + f"'{d[0]}'"
    else:
        return "in" + str(tuple(d))
