#!/usr/bin/python3
# -*- coding: utf-8 -*-

import functools
import json
import queue
import signal
import subprocess
import time
from threading import Thread

import redis

from Ctx import Ctx
from Frames.DbWorkersStatus import DbWorkersStatus


# https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html
# https://redis.readthedocs.io/en/stable/examples.html

# Obsługa sygnału SIGINT
def signal_handler(sig, frame, ctx):
    print("Exiting...")
    ctx.running_disable()


def is_json(raw_frame):
    try:
        json.loads(raw_frame)
    except ValueError as e:
        return False
    return True


# Funkcja obsługująca otrzymane ramki JSON
def process_frame(raw_frame, ctx):
    json_frame = json.loads(raw_frame)
    frame_type = json_frame.get("frameType")
    if frame_type == "dbWorkerStatus":
        if ctx.set_db_worker_status(json_frame):
            ctx.redis_conn.publish(ctx.redis_config.channel_name, ctx.get_db_workers_status)


def begin_run_db_workers(ctx):
    processes = [
        subprocess.Popen(
            [ctx.db_worker_status_config.db_worker_path, "-c", ctx.db_worker_status_config.db_worker_config]) for _ in
        range(ctx.db_worker_status_config.start_db_workers)
    ]


class ReaderThread(Thread):
    def __init__(self, name, ctx, sender):
        super().__init__()
        self._name = name
        self._ctx = ctx
        self.__sender = sender
        self.__pubsub = self._ctx.redis_conn.pubsub()
        self.__pubsub.psubscribe(self._ctx.redis_config.channel_name)

    def run(self) -> None:
        while self._ctx.running:
            message = self.__pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                self.__sender.process(message)
                print(f"[{self._name}] :  ({self._ctx.running}) : {message}")
            time.sleep(0.001)

        print(f"EXIT - [{self._name}] : ({self._ctx.running})")


class SenderThread(Thread):
    def __init__(self, name, ctx):
        super().__init__()
        self.__name = name
        self.__ctx = ctx
        self.__mq = queue.Queue()

    def run(self) -> None:
        while self.__ctx.running:
            if not self.__mq.empty():
                message = self.__mq.get_nowait()
                raw_frame = message["data"].decode()
                if is_json(raw_frame):
                    json_frame = json.loads(raw_frame)
                    frame_type = json_frame.get("frameType")
                    if frame_type == "dbWorkerStatus":
                        #print(f"[{self.__name}] : ({self.__ctx.running}) : {message}")
                        if self.__ctx.set_db_worker_status(json_frame):
                            self.__ctx.redis_conn.publish(self.__ctx.redis_config.channel_name, self.__ctx.get_db_workers_status)
                            print(f"[{self.__name}] : ({self.__ctx.running}) : {self.__ctx.get_db_workers_status}")

                self.__mq.task_done()

                if self.__ctx.recalculate_statuses():
                    self.__ctx.redis_conn.publish(self.__ctx.redis_config.channel_name, self.__ctx.get_db_workers_status)
                    print(f"[{self.__name}.STATUSES] : ({self.__ctx.running}) : {self.__ctx.get_db_workers_status}")

            time.sleep(0.001)
        print(f"EXIT - [{self.__name}] : ({self.__ctx.running})")

        self.__mq.join()

    def process(self, message):
        self.__mq.put_nowait(message)


def main():
    print("START programu")

    main_ctx = Ctx()

    # Ustawienie obsługi sygnału SIGINT
    siginit_handler = functools.partial(signal_handler, ctx=main_ctx)
    signal.signal(signal.SIGINT, siginit_handler)

    main_ctx.redis_conn = redis.Redis(host=main_ctx.redis_config.host, port=main_ctx.redis_config.port,
                                      password=main_ctx.redis_config.password)

    begin_run_db_workers(main_ctx)

    threads = []

    main_ctx.running_enable()

    st = SenderThread("SENDER", main_ctx)

    threads.append(ReaderThread("READER", main_ctx, st))
    threads.append(st)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("KONIEC programu")


if __name__ == '__main__':
    main()
