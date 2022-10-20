import datetime

# metaclass类
from controller.base import controller_metaclass

# sql
from .base import *
from common.models.url_data import UrlDatum
from common.models.user_log import UserLog

# notify
from notify.wechat import Wechat
from notify.telegram_ import Telegram


class Url_data_do(controller_metaclass):
    """
    这个类用来对数据库的data_url表进行处理和逻辑方法
    :param indata,dict,示例
    {
        'name':{
            'mainkey':{
                'key':'value'
            }
        }
    }
    """

    def __init__(self, indata: dict) -> None:
        self.indata = indata
        # self.enable_dict = enable_dict
        self.notify = {}

    def go_Url_data_do(self, user_enable_dict: dict):
        for i, d in self.indata.items():
            if d:
                m = self._get(i)
                _current_contents, _current0_today, _today_contents, _date = (
                    m.__dict__.get("current_contents"),
                    m.current0_today,
                    m.today_contents,
                    m.date,
                )  # 获取数据库中存的数据
                # 判断第一次添加和
                _change_data = compare_dict(
                    d, list_content(_current_contents), list_content(_current0_today)
                )

                # 查询到历史单据的情况
                if _date != datetime.date.today():
                    _current0_today_insert = add_current_contents(
                        str(d), list_content(_today_contents)
                    )
                else:
                    _current0_today_insert = add_current_contents(
                        _current0_today, _change_data
                    )

                _today_contents_insert = (
                    add_current_contents(_today_contents, _change_data)
                    if _date == datetime.date.today() and _current_contents
                    else "{}"
                )

                if _change_data:
                    self.notify[i] = list(_change_data.values())
                    _n_update = 1

                    # 是否插入user_log表
                    if i in user_enable_dict:
                        self._insert_into_user_log(
                            user_enable_dict.get(i),
                            i,
                            _change_data,
                        )
                else:
                    _n_update = 0

                self._insert(
                    i,
                    str(d),
                    _current0_today_insert,
                    _today_contents_insert,
                    _n_update,
                )

    def _get(self, name: str):
        session = Session()
        try:
            _contents_model = (
                session.query(UrlDatum)
                .filter_by(name=name, enable=1, date=get_time())
                .all()[0]
            )
        except:
            try:
                # _yesterday = (
                #     datetime.datetime.now() + datetime.timedelta(days=-1)
                # ).strftime("%Y-%m-%d")

                _contents_model = (
                    session.query(UrlDatum)
                    .filter(
                        UrlDatum.name == name,
                        # UrlDatum.enable == 0,
                        UrlDatum.date < datetime.date.today(),
                    )
                    .order_by(UrlDatum.date.desc())
                    .limit(1)
                    .all()[0]
                    # .order_by(UrlDatum.date)
                )
                session2 = Session()
                session2.add(UrlDatum(name=name))
                _contents_model_ = (
                    session2.query(UrlDatum)
                    .filter(
                        UrlDatum.name == name,
                        # UrlDatum.enable == 0,
                        UrlDatum.date < datetime.date.today(),
                    )
                    .order_by(UrlDatum.date.desc())
                    .limit(1)
                    .all()[0]
                )
                _contents_model.need_update = 0
                # _contents_model.enable = 0
                session2.add(_contents_model_)
                session2.commit()
                session2.close()
            except:
                session.add(UrlDatum(name=name))
                session.commit()
                _contents_model = (
                    session.query(UrlDatum)
                    .filter_by(name=name, enable=1, date=get_time())
                    .all()[0]
                )
        session.close()
        return _contents_model

    def _insert(
        self,
        name: str,
        current_data: str,
        current0_data: str,
        today_data: str,
        _n_update: int,
    ):
        session = Session()
        # url_data的操作
        _url_need_model = (
            session.query(UrlDatum)
            .filter_by(name=name, enable=1, date=get_time())
            .all()[0]
        )
        _url_need_model.current_contents = current_data
        _url_need_model.current0_today = current0_data
        _url_need_model.today_contents = today_data
        _url_need_model.last_update = datetime.datetime.now().replace(microsecond=0)
        _url_need_model.need_update = _n_update
        session.add(_url_need_model)
        try:
            session.commit()
            session.close()
            return True
        except:
            session.rollback()
            session.close()
            return False

    def _insert_into_user_log(self, user_list: list, name: str, change_data: dict):
        """
        :param user_list,需要更新的user用户名的list
        :param change_data,示例 {i: list(_change_data.values())}
        """
        session = Session()
        # 返回一个list，里面为元组
        _all_current_contents = session.execute(
            "SELECT name,current_contents FROM user_log WHERE name IN {}".format(
                tuple(user_list),
            )
        ).fetchall()
        _new_all_current_contents = self._handle_select_data_user(
            _all_current_contents, name, change_data
        )
        for i, d in _new_all_current_contents.items():
            _user_m = session.query(UserLog).filter_by(name=i).first()
            _user_m.last_update = datetime.datetime.now().replace(microsecond=0)
            _user_m.current_contents = str(d.get("new_current_contents"))
            session.add(_user_m)
        session.commit()

    def _handle_select_data_user(
        self,
        all_current_contents: list,
        name: str,
        change_contetns: dict,
    ):
        """
        这个函数用来处理从user_log拿到的数据,并将变化的数据和原数据进行组合
        :param _all_current_contents,查询到结果的fetchall
        :param
        """

        # 需要返回的数据，current_contents，new_current_contents都为str类型
        _data = {}
        # _all_current_contents转化为dict
        _handle_o_data = [dict(zip(item.keys(), item)) for item in all_current_contents]

        for i in _handle_o_data:
            _data[i.get("name")] = {}
            _data[i.get("name")]["current_contents"] = _data[i.get("name")][
                "new_current_contents"
            ] = list_content(i.get("current_contents"))
            _data[i.get("name")]["new_current_contents"][name] = list_content(
                add_current_contents(
                    str(_data[i.get("name")]["current_contents"].get(name)),
                    change_contetns,
                )
            )

        return _data
