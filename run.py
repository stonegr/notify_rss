from common.config_do import Config_do
from common.spider_parse import Spider_parser
from controller.url_data import Url_data_do
from controller.user_log import User_data_do
from controller.base import *
from base.aps import Aps_do
from common.models.url_data import UrlDatum
from base.thread import Thread
from base.logging_ import logger


class Task_do:
    """ """

    def __init__(self) -> None:
        pass

    def init_data(self):
        # 通过cron，对data和usre的任务进行分类
        _list = Config_do.get_task_l(["data", "user"])

        # 通过enable和disable对url和user进行分类
        _list_status = Config_do.get_status_tasks_l(["data", "user"])
        # 对url类型数据，进行初始化处理
        check_status_task(_list_status.get("data"), UrlDatum)
        # 对user类型数据，进行初始化处理
        check_status_user(_list_status.get("user"), UserLog)

        # 对usre进行数据处理，url中需要更新的user表name
        _user_enable_dict = Config_do.get_user_enable()

        return _list, _user_enable_dict

    def go_url_do(self, force=False):
        _list, _user_enable_dict = self.init_data()
        # print(_list.get("data"))
        if not force:
            a = Aps_do()
            a.add_jobs(
                self.url_do,
                _list.get("data"),
                _user_enable_dict,
                task_cate="url_data",
            )
            a.add_jobs(
                self.user_do,
                _list.get("user"),
                task_cate="user",
            )
            a.start_job()
        else:
            self.url_do(Config_do.get_enable_data(), "all", _user_enable_dict)

    def test_url(self, *args: list, need_l=1):
        """
        :params args 代表你要测试的data的名称
        :params need_l 需要的items数,默认显示一个,all表示所有
        """
        _data_tmp = {}
        for i in args:
            _data_tmp[i] = Config_do.get_self(Config_do.config, ["data", i])
        # print(_data_tmp)
        _s = Spider_parser(
            Config_do.config,
            Config_do.get_self(Config_do.config, ["config", "asyncio_Semaphore"], 10),
            _data_tmp,
        )
        _items = _s.go_Spider_parser()
        # print(_items)

        # _print_data = ""
        for i, d in _items.items():
            if need_l == "all":
                print(i, d, "\n---")
            else:
                print(i, list(d.items())[0:need_l], "\n---")
        # print(list(_items[n].items())[0])
        # logger.info(_items)

    def url_do(self, do_data: dict, name: str, user_enable_dict: dict):
        """
        对url表中的数据进行操作
        :param do_data,传入示例
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
        :param name,定时任务的名称
        :param user_enable_dict,url中需要更新的user表name
        """
        logger.info("----start_fetch name: [{}]----".format(name))
        _start = time.time()
        # 数据的抓取和分析
        s = Spider_parser(
            Config_do.config,
            Config_do.get_self(Config_do.config, ["config", "asyncio_Semaphore"], 10),
            do_data,
        )
        d = s.go_Spider_parser()
        # 数据的入库处理
        url_data_do = Url_data_do(d)
        url_data_do.go_Url_data_do(user_enable_dict)

        # 数据的通知
        if url_data_do.notify:
            self.data_notify(url_data_do.notify)

        logger.info(
            "----finish_fetch name: [{}] time: {:.2f} s----".format(
                name, float(time.time() - _start)
            )
        )

    def user_do(self, user_d: dict, name: str):
        """
        :param user_d,示例
        Config_do.config.get("user")
        """
        logger.info("----start user_notify users: [{}]----".format(list(user_d.keys())))
        _start = time.time()
        u = User_data_do(user_d)
        u.go_User_data_do()
        if u.notify_user:
            self.user_notify(u.notify_user)
        logger.info(
            "----finish user_notify users: [{}] time: {:.2f} s----".format(
                list(user_d.keys()),
                float(time.time() - _start),
            )
        )

    def data_notify(self, data: dict, *args):
        """
        多线程的通知方法
        :pram data,{name:list(数据库取的值不带mainkey)}
        """
        _tasks = []
        for i, d in data.items():
            _tasks.append(
                {
                    "func": notify,
                    "args": ({i: d}, "url_title", *args),
                }
            )
        t = Thread(_tasks)
        t.go_thread()

    def user_notify(self, data: dict, *args):
        """
        多线程的通知方法,user
        :pram data,{user:{name:list(数据库取的值不带mainkey)}}
        """
        _tasks = []
        for i, d in data.items():
            _tasks.append(
                {
                    "func": notify,
                    "args": (
                        d,
                        "user_title",
                        Config_do.get_self(
                            Config_do.config,
                            ["user", i, "methods"],
                            Config_do.get_self(Config_do.config, ["config", "methods"]),
                        ),
                    ),
                }
            )
        t = Thread(_tasks)
        t.go_thread()
