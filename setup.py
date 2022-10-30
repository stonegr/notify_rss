import argparse, os, sys
from common.config_do import Config_do
from base.base import *

import shutil

if getattr(sys, "_MEIPASS", False):
    _name = "static"

    _curr = os.path.join(os.path.abspath("."), _name)
    _ori = getattr(sys, "_MEIPASS") + os.sep + _name

    # print(getattr(sys, "_MEIPASS"), _curr)
    # print(os.listdir(_ori))

    if not os.path.exists(_curr):
        shutil.copytree(_ori, _curr)


def start(force=False):
    from run import Task_do

    t = Task_do()
    t.go_url_do(force)


def cs_item(*args, need_l=1):
    from run import Task_do

    t = Task_do()
    t.test_url(*args, need_l=need_l)


parser = argparse.ArgumentParser(description="welcome to notify_rss")
parser.add_argument(
    "-c",
    "--config",
    # required=True,
    help="configuration file path",
)
parser.add_argument(
    "-t",
    "--test",
    nargs="+",
    help="Test the items in your configuration file, you can choose one or more",
)
parser.add_argument(
    "-ti",
    "--t_item",
    help="Select the number of items displayed when testing",
)
parser.add_argument(
    "-f",
    "--force",
    action="store_true",
    help="Force update",
)
args = parser.parse_args()

# print(os.listdir("."))
if "config.json" in os.listdir("."):
    _f_path = os.path.abspath(".") + os.sep + "config.json"
    Config_do().read_config(_f_path)
else:
    Config_do().read_config(args.config)

if args.test:
    # print(args.test)
    # print(args.t_item)
    # print(type(args.t_item))
    if args.t_item:
        try:
            _need_l = int(args.t_item)
        except:
            _need_l = str(args.t_item)  # 为all时显示全部
        cs_item(*args.test, need_l=_need_l)
    else:
        cs_item(*args.test)
else:
    if args.force:
        start(args.force)
    else:
        start()

# start()
