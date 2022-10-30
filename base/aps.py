"""
这个类用来添加定时任务
"""


from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.triggers.cron import CronTrigger

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from base.logging_ import logger
from controller.base import *

sche = BlockingScheduler(
    executors={
        "default": ThreadPoolExecutor(20),
        "processpool": ProcessPoolExecutor(5),
    },
    job_defaults={
        "coalesce": True,  # 系统原因没执行就不用执行了
        "max_instances": 5,
    },
    timezone="Asia/Shanghai",
)


class Aps_do:
    def __init__(self):
        pass

    def rm_all_jobs(self):
        sche.remove_all_jobs()

    def get_all_jobs(self):
        jobs = sche.get_jobs()
        self.old_jobs = {}
        for i in jobs:
            self.old_jobs[i.name] = i.id
        return self.old_jobs

    def add_jobs(self, func, tasks: dict, *args, **kws):
        for i, d in tasks.items():
            sche.add_job(
                func,
                CronTrigger.from_crontab(
                    i,
                    timezone="Asia/Shanghai",
                ),
                name=i,
                args=(d, i, *args),
                kws=kws,
            )
            logger.info(
                f"task_{kws.get('task_cate')}[{i}] 已添加 {get_time('%Y-%m-%d %H:%M:%S')}"
            )
        self.get_all_jobs()

    def start_job(self):
        sche.start()
