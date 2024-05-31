
class MainConfig:
    def __init__(self):
        self.__version = "0.0.1"
        self.__release_date = "30.04.2024"
        self.__config_file_path = "./db_manager.conf"

    @property
    def version(self):
        return self.__version

    @property
    def release_date(self):
        return self.__release_date

    @property
    def config_file_path(self):
        return self.__config_file_path

    @config_file_path.setter
    def config_file_path(self, path):
        self.__config_file_path = path