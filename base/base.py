from functools import wraps
import time
import sys, os

# 显示运行时间的装饰器
def print_dur_time(f):
    @wraps(f)
    def func(*args, **kws):
        s = time.time()
        f(*args, **kws)
        print(str(time.time() - s) + " s")

    return func


# mainkey默认值的处理，可能为list可能为dict
def list_dict_keys(d):
    if isinstance(d, list):
        return d
    elif isinstance(d, dict):
        return list(d.keys())


# 判断打包后的文件位置
def resource_path(relative_path=""):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__name__)))
    return os.path.join(base_path, relative_path)
