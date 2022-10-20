import datetime

# metaclass类
from controller.base import controller_metaclass

# sql
from .base import *
from common.models.user_log import UserLog


class User_data_do(controller_metaclass):
    """
    :param user_d,示例
    Config_do.config.get("user")
    self.notify_user,示例
    {
        'stone':{},
        'stone2':{}
    }
    """

    def __init__(self, user_d: dict) -> None:
        self.user_d = user_d
        self.notify_user = {}

    def go_User_data_do(self):
        for i, d in self.user_d.items():
            # 创建本地的dict
            if i not in self.notify_user:
                self.notify_user[i] = {}
            m = self._get(i)  # 获取user的moudle
            _current_contents = m.current_contents
            if _current_contents:
                for i_, d_ in list_content(_current_contents).items():
                    self.notify_user[i][i_] = list(d_.values())

            # 刷新current_data
            session = Session()
            _update_model = session.query(UserLog).filter(UserLog.name == i).all()[0]
            _update_model.current_contents = ""
            _update_model.last_update = datetime.datetime.now().replace(microsecond=0)
            session.add(_update_model)
            session.commit()
            session.close()

    def _get(self, name: str):
        session = Session()
        _user_m = session.query(UserLog).filter(UserLog.name == name).all()
        session.close()

        return _user_m[0]

    def _insert(self):
        pass
