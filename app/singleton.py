import threading


class SingletonMeta(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        self._locker = threading.Lock()
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            with self._locker:
                if self.__instance is None:
                    self.__instance = super().__call__(*args, **kwargs)
        return self.__instance
