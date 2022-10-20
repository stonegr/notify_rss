from functools import wraps
import time

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
