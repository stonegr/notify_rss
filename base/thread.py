import threading


class Thread:
    """
    使用这个类,发送lis的单个格式
    {func,args,kws}, kws中加入lock表示需不要锁定,为false时,
    args中有数组的时候，用(i,)
    表示这个进程不需要锁定,需要锁定时，同类型任务都得添加


    """

    threads = []

    def __init__(self, lis: list):
        self.lis = lis

    def go_thread(self):
        self.__creat_c()
        self.__start_t()
        self.__funcall_w()

    def __creat_c(self):
        """
        创建线程
        """
        for i in self.lis:
            x = "thread%s" % format(self.lis.index(i) + 1)
            globals()[x] = _myThread(
                i.get("func"), *i.get("args", ()), **i.get("kws", {})
            )
            # exec(f'{x}=myThread(*i)')
            self.threads.append(globals()[x])

    def __start_t(self):
        """
        开启线程
        """
        for i in range(len(self.lis)):
            # exec(f'thread{i+1}.start()')
            globals()[f"thread{i+1}"].start()

    def __funcall_w(self):
        """
        加入等待所有任务完成
        """
        for t in self.threads:
            t.join()


class _myThread(threading.Thread):
    """
    上一个类的辅助类
    """

    threadLock = threading.Lock()

    def __init__(self, func, *args, **kws):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.kws = kws

    def run(self):
        if self.kws.get("lock"):
            self.kws.pop("lock")
            self.threadLock.acquire()
            self.run_fun()
            self.threadLock.release()
        else:
            self.run_fun()

    def run_fun(self):
        self.func(*self.args, **self.kws)
