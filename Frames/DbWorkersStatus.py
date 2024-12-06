import json
import time


class DbWorkersStatus:
    def __init__(self):
        self.counter_dbworkers = 0
        self.statuses = {}

    def set_status_json(self, json_frame):

        out_status = False

        db_w_s = DbWorkerStatus()
        db_w_s.json_decode(json_frame)
        #db_w_s.show()

        elem = self.statuses.get(db_w_s.get_pid)

        if elem is None:
            self.statuses[db_w_s.get_pid] = db_w_s
            out_status = True
        else:

            if self.statuses[db_w_s.get_pid].get_status != db_w_s.get_status:
                out_status = True

            self.statuses[db_w_s.get_pid].set_status(db_w_s.get_status)

        return out_status

    def get_json(self):
        statuses = []
        for pid in self.statuses:
            s = {'status': self.statuses[pid].get_status, 'pid': self.statuses[pid].get_pid}
            statuses.append(s)

        out_json = {"version": "1.0",
                    "frameType": "dbWorkersStatus",
                    "data": {"numberDbWorkers": len(statuses),
                             "statuses": statuses
                             }
                    }
        return json.dumps(out_json)

    def statuses_recalculate(self, interval):
        ts = time.time()
        change = False

        tmp_statuses = self.statuses.copy()

        for pid in self.statuses:
            if ts - self.statuses[pid].get_ts > interval:
                change = True
                tmp_statuses.pop(pid)

        if change:
            self.statuses = tmp_statuses.copy()

        return change

    def show(self):
        print("Statusy DB workerow:")
        for pid in self.statuses:
            self.statuses[pid].show()


#{"frameType":"dbWorkerStatus","version":"1.0","pid":206039,"data":{"status":"start"}}

class DbWorkerStatus:
    def __init__(self):
        self.__pid = 0
        self.__status = "none"
        self.__ts = time.time()

    def set_status(self, status):
        self.__ts = time.time()
        self.__status = status

    def json_decode(self, json_frame):
        self.__pid = json_frame.get("pid")
        self.__status = json_frame.get("data").get("status")
        self.__ts = time.time()

    @property
    def get_pid(self):
        return self.__pid

    @property
    def get_status(self):
        return self.__status

    @property
    def get_ts(self):
        return self.__ts

    def show(self):
        print(f"PID: {self.__pid}, STATUS: {self.__status}, TS: {self.__ts}")
