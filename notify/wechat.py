import requests, os
import json

from notify.base import Notifymataclass

from functools import wraps
from copy import deepcopy

# # 以下内容需要删除
# import sys

# sys.path.append("..")
"""
Config_do.get_self(Config_do.config, ["tz", "wechat", "wecom_aid"])
Config_do.get_self(Config_do.config, ["tz", "wechat", "wecom_cid"])
Config_do.get_self(Config_do.config, ["tz", "wechat", "wecom_secret"])

"""
# #


# path = os.path.abspath(
#     os.path.join(os.path.dirname(os.path.abspath(__file__)), "../static/secreat")
# )
path = "static/secreat"

# 检测获取token，从文件
# def _get_token(f):
#     @wraps(f)
#     def func(*args, **kws):
#         if os.path.exists(path + os.sep + "access_token.txt"):
#             with open(path + os.sep + "access_token.txt", "r", encoding="utf-8") as ft:
#                 t = ft.read().strip()
#             ft.close()
#         else:
#             t = Wechat._wx_token()
#         status = f(t, *args, **kws)
#         if status.get("errcode") != 0:
#             t = Wechat._wx_token()
#             status = f(t, *args, **kws)

#     return func


# 检测获取token，从内存
def _get_token(f):
    @wraps(f)
    def func(*args, **kws):
        if "access_token" in locals().keys():
            t = globals()["access_token"]
        else:
            t = Wechat._wx_token()
        status = f(t, *args, **kws)
        if status.get("errcode") != 0:
            t = Wechat._wx_token()
            status = f(t, *args, **kws)

    return func


class Wechat(Notifymataclass):
    def __init__(self, wecom_aid, wecom_cid, wecom_secret):
        self.wecom_aid = wecom_aid
        Wechat.wecom_cid = wecom_cid
        Wechat.wecom_secret = wecom_secret

    @_get_token
    def fs_tz(
        access_token,
        self,
        text,
        wecom_touid,
    ):
        """
        微信text
        """
        if access_token and len(access_token) > 0:
            send_msg_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
            data = {
                "touser": wecom_touid,
                "agentid": self.wecom_aid,
                "msgtype": "text",
                "text": {"content": text.rstrip()},
                "duplicate_check_interval": 600,
            }
            response = requests.post(send_msg_url, data=json.dumps(data))
            return response.json()
        else:
            return False

    def content_format(self, contents_deep: dict, title: str):
        contents = deepcopy(contents_deep)
        content = f"{title}\n\n"  # 需要发送的消息
        for i, d in contents.items():
            content_tmp = "{title}\n".format(title=i)
            for i_ in d:
                if {"link", "title"} == ({"link", "title"} & set(i_.keys())):
                    content_tmp += self._link(i_.get("title"), i_.get("link"), 8)
                    i_.pop("title")
                    i_.pop("link")
                for name_, data_ in i_.items():
                    if self.is_link(data_):
                        content_tmp += (
                            " " * 8
                            + f"{name_}: "
                            + self._link(
                                "link",
                                data_,
                            )
                        )
                    else:
                        content_tmp += " " * 8 + f"{name_}: " + data_ + "\n\n"
            content_tmp += "-" * 38 + "\n"
            # content_tmp += "-" * 3 + "\n"
            content += content_tmp
        return content

    def _link(self, contents, link, sep=0, ends="\n"):
        return '{sep}<a href="{url}">{url_title}</a>{ends}'.format(
            sep=" " * sep,
            url=link,
            url_title=contents,
            ends=ends,
        )

    @classmethod
    def _wx_token(cls):
        """
        获取企业微信token
        """

        get_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={cls.wecom_cid}&corpsecret={cls.wecom_secret}"
        response = requests.get(get_token_url).content
        access_token = json.loads(response).get("access_token")

        # 储存到文件
        # with open(path + os.sep + "access_token.txt", "w", encoding="utf-8") as f:
        #     f.write(access_token + "\n")
        # f.close()

        # 储存到内存
        globals()["access_token"] = access_token

        return access_token
