from threading import Lock

import redis

from Conf.DBWorkersStatusConfig import DBWorkersStatusConfig
from Conf.MainConfig import MainConfig
from Conf.RedisConfig import RedisConfig
from Frames.DbWorkersStatus import DbWorkersStatus


class Ctx:
    def __init__(self):
        self.__main_config = MainConfig()
        self.__redis_config = RedisConfig()
        self.__db_worker_status_config = DBWorkersStatusConfig()

        self.__db_workers_status = DbWorkersStatus()
        self.__running = False
        self.__redis_conn = None

        self.__lock = Lock()

    @property
    def main_config(self):
        return self.__main_config

    @property
    def redis_config(self):
        return self.__redis_config

    @property
    def redis_conn(self):
        return self.__redis_conn

    @redis_conn.setter
    def redis_conn(self, conn):
        self.__redis_conn = conn

    @property
    def running(self):
        with self.__lock:
            return self.__running

    def running_enable(self):
        with self.__lock:
            self.__running = True

    def running_disable(self):
        with self.__lock:
            self.__running = False

    def set_db_worker_status(self, db_worker_status):
        return self.__db_workers_status.set_status_json(db_worker_status)

    @property
    def get_db_workers_status(self):
        return self.__db_workers_status.get_json()

    def get_check_status_interval(self):
        return self.__db_worker_status_config.check_interval

    def recalculate_statuses(self):
        return self.__db_workers_status.statuses_recalculate(self.get_check_status_interval())

    @property
    def db_worker_status_config(self):
        return self.__db_worker_status_config
