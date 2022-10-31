import abc
from typing import Union


class Notifymataclass(abc.ABC):
    def fs(self, contents: dict, user: str, title: str):
        if contents:  # 为空的判断
            content_ = self.content_format(contents, title)
            if isinstance(content_, list):
                for i in content_:
                    self.fs_tz(i, user)
            else:
                self.fs_tz(content_, user)

    @abc.abstractmethod
    def fs_tz(self, content, user):
        pass

    @abc.abstractmethod
    def content_format(self, contents: dict, title: str):
        pass

    def _title(self, contents, ends="\n"):
        pass

    def _str(self, contents, ends="\n"):
        pass

    # 这个用来判断获取到的文本是否是一个链接
    def is_link(self, s: str) -> bool:
        _link_like = (
            "http",
            "magnet",
        )
        if s.startswith(_link_like):
            return True
        else:
            return False

    def _link(self, contents, link, sep=0, ends="\n"):
        pass
