class SingletonBase:
    _instance = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
            print(f"Initialized singleton {cls.__name__}")
        return cls._instance

