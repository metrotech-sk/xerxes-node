#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pymongo import MongoClient, InsertOne, DeleteMany, ReplaceOne, UpdateOne
from pymongo.collection import Collection
from typing import Dict
from xerxes_protocol import XerxesRoot, ChecksumError, MessageIncomplete, Leaf
from yaml import load
import dotenv

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import logging
import os
import time
import datetime
import string
import random

log = logging.getLogger(__name__)
dotenv.load_dotenv()


def generate_random_key():
    return "".join(
        random.choices(
            string.ascii_letters + string.digits, k=random.randint(3, 8)
        )
    )


def generate_random_value():
    return "".join(
        random.choices(
            string.ascii_letters + string.digits, k=random.randint(5, 15)
        )
    )


def generate_random_dict(level=0, max_level=5):
    if (
        level >= max_level or random.random() < 0.3 and level > 1
    ):  # Stop condition to limit depth
        return generate_random_value()

    num_fields = random.randint(5, 10)
    random_dict = {}
    for _ in range(num_fields):
        key = generate_random_key()
        if (
            random.random() < 0.5 and level < max_level - 1
        ):  # 50% chance to create a nested dictionary
            random_dict[key] = generate_random_dict(level + 1, max_level)
        else:
            random_dict[key] = generate_random_value()
    return random_dict


# Function to generate a dictionary with 3-5 levels deep
def generate_dictionary():
    max_level = random.randint(3, 5)
    return generate_random_dict(0, max_level)


class Worker:
    def __init__(self, collection: Collection):
        self.collection = collection

    def spin(self):
        while True:
            time.sleep(1)
            data = []
            for i in range(10):

                data.append(
                    # generate random dictionary:
                    generate_dictionary()
                )
            ops = []
            for d in data:
                log.debug(d)
                d.update(
                    {
                        "time": {
                            "epoch": time.time(),
                            "datetime": datetime.datetime.now().isoformat(
                                timespec="seconds"
                            ),
                        }
                    }
                )
                ops.append(InsertOne(d))

            log.info("performing bulk write")
            result = self.collection.bulk_write(ops, ordered=False)
            log.info(result)


if __name__ == "__main__":
    config: Dict
    # show time in log
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    with open("config.yaml") as f:
        config = load(f, Loader=Loader)

    log.info(config)
    database = MongoClient(os.getenv("XERXES_MONGO_URI")).get_database("test")
    log.debug(database)
    col: Collection = database["PRJ-16"]
    log.debug(col)

    col.drop()

    w = Worker(collection=col)
    log.debug(w)
    w.spin()
