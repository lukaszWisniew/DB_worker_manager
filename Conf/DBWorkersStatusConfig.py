class DBWorkersStatusConfig:
    def __init__(self):
        self.__check_interval = 3
        self.__start_db_workers = 3
        self.__max_db_workers = 100
        self.__db_worker_path = "/home/lukas/Develop/Reaktywacja/Amadeus/DB_worker/src/DB_worker"
        self.__db_worker_config = "/home/lukas/Develop/Reaktywacja/Amadeus/DB_worker/conf/db_worker.conf"

    @property
    def check_interval(self):
        return self.__check_interval

    @check_interval.setter
    def check_interval(self, interval):
        self.__check_interval = interval

    @property
    def db_worker_path(self):
        return self.__db_worker_path

    @property
    def db_worker_config(self):
        return self.__db_worker_config

    @property
    def start_db_workers(self):
        return self.__start_db_workers