class RedisConfig:
    def __init__(self):
        self.__host_name = '10.25.10.128'
        self.__port = 6379
        self.__password = 'nsYSmKVlG'
        self.__channel_name = "s_w_bus"

    @property
    def host(self):
        return self.__host_name

    @property
    def port(self):
        return self.__port

    @property
    def password(self):
        return self.__password

    @property
    def channel_name(self):
        return self.__channel_name
