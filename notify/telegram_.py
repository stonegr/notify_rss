import telegram, re
from telegram.utils.request import Request
from typing import Union
from copy import deepcopy

from notify.base import Notifymataclass


class Telegram(Notifymataclass):
    def __init__(self, token):
        self.token = token

    def fs_tz(
        self,
        text,
        chat_id: Union[str, list],
        proxy=True,
        lx="markdownv2",
    ):
        """
        发送文字，用\n换行,lx=html,markdown,markdownv2
        """

        if proxy:
            dl = Request(proxy_url="socks5://127.0.0.1:30808")
            bot = telegram.Bot(token=self.token, request=dl)
        else:
            bot = telegram.Bot(token=self.token)
        if lx == "":
            lx_ = ""
        else:
            lx_ = lx.upper()
        for i in chat_id.split(","):
            bot.send_message(
                chat_id=i,
                text=text.rstrip(),
                parse_mode=lx_,
                disable_web_page_preview=True,
                timeout=5,
            )

    def content_format(self, contents_deep: dict, title: str):
        contents = deepcopy(contents_deep)
        # 需要发送的消息
        content = self._title(self._str_formart(title), "\n\n")
        # 条目的遍历
        for i, d in contents.items():
            content_tmp = self._title(self._str_formart(i))
            for i_ in d:
                if {"link", "title"} == ({"link", "title"} & set(i_.keys())):
                    content_tmp += self._link(
                        self._str_formart(i_.get("title")),
                        i_.get("link"),
                        8,
                    )
                    i_.pop("title")
                    i_.pop("link")
                for name_, data_ in i_.items():
                    if self.is_link(data_):
                        content_tmp += (
                            " " * 8
                            + self._str_formart(name_)
                            + ": "
                            + self._link(
                                "link",
                                data_,
                            )
                        )
                    else:
                        content_tmp += (
                            " " * 8
                            + self._str_formart(name_)
                            + ": "
                            + self._str_formart(data_)
                            + "\n\n"
                        )
            content_tmp += "\-" * 62 + "\n"
            # content_tmp += "\-" * 3 + "\n"
            content += content_tmp
        return content

    def _title(self, contents, ends="\n"):
        return f"*{contents}*{ends}"

    def _link(self, contents, link, sep=0, ends="\n"):
        return "{}[{}]({}){}".format(" " * sep, contents, link, ends)

    def _str_formart(self, s: str):
        title_partern = re.compile("([\_\*\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!\>\<])")
        # re.sub(title_partern, "\\\\\\1", s)
        # re.sub(title_partern, r"\\\1", s)
        return re.sub(title_partern, "\\\\\g<1>", s)
