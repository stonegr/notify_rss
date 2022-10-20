import json, os


class Config_do:
    @classmethod
    def read_config(cls, f_path: str):
        """
        读取json配置文件
        """
        cls.config = cls.r_json(f"{f_path}")

    # 获取配置并设置默认值
    @staticmethod
    def get_self(c, l: list = [], d=""):
        """
        获取配置文件的默认值
        :param c,json格式的配置文件
        :param l,获取值的路劲
        :param d,获取错误时的默认值
        """
        try:
            x = c
            for i in l:
                x = x[i]
        except:
            x = d
        return x

    @classmethod
    def get_enable_data(cls):
        _tmp_dict = {}
        for i, d in cls.config["data"].items():
            if d["enable"] == True:
                _tmp_dict[i] = d
        return _tmp_dict

    @classmethod
    def get_task_l(cls, col_l: list):
        """
        获取需要添加的计划任务
        col:["data", "user"]

        返回值:
        {
            "data": {
                "0/30 0,6-23 * * *": {
                    "p3terx": {
                        "type": "rss",
                        "enable": True,
                        "url": "https://p3terx.com/feed/",
                        "kws": {"proxy": True, "timeout": 10},
                        "cron": "0/30 0,6-23 * * *",
                        "mainkey": "link",
                    }
                },
                "user": {
                    "0/2 * * * *": {
                        "stone2": {
                            "enable": True,
                            "need_urls": ["p3terx", "nn.ci", "脑洞乌托邦", "方的言", "stone记"],
                            "methods": ["wechat", "telegram"],
                            "cron": "0/2 * * * *",
                        }
                    }
                },
            }
        }
        """
        _enable_key = Config_do.get_status_tasks_l(col_l)
        url_jobs = {}
        data_cron = cls.get_self(cls.config, ["config", "data_cron"], "0/30 * * * *")
        for item in col_l:
            url_jobs[item] = {}
            for i, d in cls.config.get(item).items():
                if i in _enable_key[item]["enable"]:
                    cron_ = cls.get_self(d, ["cron"], data_cron)
                    if cron_ not in url_jobs[item]:
                        url_jobs[item][cron_] = {}
                    url_jobs[item][cron_][i] = d
        return url_jobs

    @classmethod
    def get_status_tasks_l(cls, col_l: list) -> dict:
        """
        获取需要添加的计划任务
        col:["data", "user"]

        返回值:
        {
            "data": {
                "enable": ["p3terx"],
                "disable": [],
            },
            "user": {
                "enable": ["stone", "stone2"],
                "disable": [],
            },
        }
        """
        url_jobs = {}
        for item in col_l:
            url_jobs[item] = {}
            url_jobs[item]["enable"] = []
            url_jobs[item]["disable"] = []
            for i, d in cls.config.get(item).items():
                cron_ = cls.get_self(d, ["enable"])
                if cron_:
                    url_jobs[item]["enable"].append(i)
                else:
                    url_jobs[item]["disable"].append(i)
        return url_jobs

    @classmethod
    def get_user_enable(cls):
        """
        遍历user，以data.name为基准创建字典
        返回值:
        {
            "p3terx": ["stone", "stone2"],
            "nn.ci": ["stone", "stone2"],
        }
        """
        user_job = {}
        for i, d in cls.config.get("user").items():
            for i_ in d.get("need_urls"):
                if i_ not in user_job:
                    user_job[i_] = []
                user_job[i_].append(i)
        return user_job

    @staticmethod
    def r_json(lj):
        """
        读取json到字典
        """
        f = open(f"{lj}", "r", encoding="utf-8", newline="")
        char_ = f.read()
        f.close()
        return json.loads(char_)


# Config_do().read_config("config")
