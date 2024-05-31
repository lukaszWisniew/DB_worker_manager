#!/usr/bin/python3
# -*- coding: utf-8 -*-

import asyncio
import functools
import json
import signal
import subprocess

import redis.asyncio as redis

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


async def reader(channel: redis.client.PubSub, ctx):
    message = await channel.get_message(ignore_subscribe_messages=True)
    if message is not None:
        print(f"(Reader) Message Received: {message}")
        raw_frame = message["data"].decode()
        if is_json(raw_frame):
            await process_frame(raw_frame, ctx)


# Funkcja obsługująca otrzymane ramki JSON
async def process_frame(raw_frame, ctx):
    json_frame = json.loads(raw_frame)
    frame_type = json_frame.get("frameType")
    print(f"Frame type: {frame_type}")
    if frame_type == "dbWorkerStatus":
        if ctx.set_db_worker_status(json_frame):
            await ctx.redis_conn.publish("s_w_bus", ctx.get_db_workers_status)


async def begin_run_db_workers(ctx):
    processes = [
        subprocess.Popen(
            [ctx.db_worker_status_config.db_worker_path, "-c", ctx.db_worker_status_config.db_worker_config]) for _ in
        range(ctx.db_worker_status_config.start_db_workers)
    ]


async def main():
    main_ctx = Ctx()

    redis_conn = redis.Redis(host='10.25.10.115', port=6379, password='nsYSmKVlG')

    main_ctx.redis_conn = redis_conn

    print("START programu")

    # Ustawienie obsługi sygnału SIGINT
    siginit_handler = functools.partial(signal_handler, ctx=main_ctx)
    signal.signal(signal.SIGINT, siginit_handler)

    main_ctx.running_enable()

    await begin_run_db_workers(main_ctx)

    async with redis_conn.pubsub() as pubsub:
        await pubsub.subscribe("s_w_bus")

        while main_ctx.running:
            future = asyncio.create_task(reader(pubsub, main_ctx))
            await future
            if main_ctx.recalculate_statuses():
                await main_ctx.redis_conn.publish("s_w_bus", main_ctx.get_db_workers_status)

            await asyncio.sleep(0.1)

        await redis_conn.aclose()
        print("KONIEC programu")


if __name__ == '__main__':
    asyncio.run(main())
