#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import datetime
from threading import Thread, Lock
import time
from typing import Dict, List
from xerxes_protocol import (
    XerxesRoot,
    ChecksumError,
    MessageIncomplete,
    Leaf,
)

from .timeutil import add_timestamp
from threading import Thread
import json
import os


log = logging.getLogger(__name__)


def safe_read_attribute(leaf: Leaf, attr):
    value = None
    try:
        while leaf.network.is_busy:
            time.sleep(0.001)
        value = leaf.__getattribute__(attr)
    except AttributeError:
        log.warning(f"Leaf {leaf.address} does not have attribute {attr}")
    except ChecksumError:
        log.warning(f"message from leaf {leaf.address} has invalid checksum")

    except MessageIncomplete:
        log.warning(f"message from leaf {leaf.address} is not complete.")

    except TimeoutError:
        log.warning(f"Leaf {leaf.address} is not responding.")

    except ValueError:
        log.warning(f"Leaf {leaf.address} returned empty data.")

    except Exception as e:
        traceback = sys.exc_info()[:3]
        log.error(f"Unexpected error: {e}, Traceback:\n{traceback}")

    finally:
        return value


class Job(Thread):
    """This is a job that will be run by worker thread.

    It will collect data from leaves and save it to file."""

    def __init__(self, leaves: List[Leaf], workdir="/tmp/xerxes", name=None):
        """Initialize job with leaves.

        Args:
            leaves (List[Leaf]): list of leaves. Each leaf should have values: Dict attribute.
            workdir (str, optional): directory to save measurements. Defaults to "/tmp/xerxes".
        """
        super().__init__()
        self.leaves = leaves
        self._workdir = workdir
        self._name = name

    def run(self):
        """Run job.

        Collect data from leaves and save it to file."""

        log.info(f"Job started [{self._name}]")
        data = {}
        for leaf in self.leaves:
            leaf_data = {}
            if leaf.values:
                for key, value in leaf.values.items():
                    value = safe_read_attribute(leaf, value)
                    leaf_data[key] = value
                    log.debug(
                        f"Leaf {leaf.label}@{hex(leaf.address)} {key}: {value}"
                    )
            
            if leaf.calls:
                for call in leaf.calls:
                    retval = leaf.__getattribute__(call)()
                    log.info(f"Leaf {leaf.label}@{hex(leaf.address)} {call}: {retval}")

            data[leaf.label] = leaf_data

        # add timestamp to data
        add_timestamp(data)
        filename_location = os.path.join(
            self._workdir,
            f"{self._name}_{datetime.datetime.now().isoformat(timespec='seconds').replace(':', '-')}.dat",
        )
        # save data to file
        with open(filename_location, "w") as f:
        # with tempfile.NamedTemporaryFile(
        #     delete=False,
        #     suffix=".dat",
        #     prefix="data_" if not self._name else self._name + "_",
        #     dir=self._workdir,
        #     mode="w",
        # ) as f:
            # pickle.dump(data, f)
            json.dump(data, f, skipkeys=True, indent=4)
            log.info(f"Data saved to {f.name}")

        log.info(f"Job finished [{self._name}]")


class Worker(Thread):
    """This is a worker thread that will periodically call job on leaves."""

    _period = None
    _leaves = []
    _active = False
    job: Job = None

    def setup(
        self,
        period: int,
        leaves: List[Leaf],
        workdir: str = "/tmp/xerxes",
        name=None,
    ):
        """Setup worker with period and leaves.

        Args:
            period (int): period in seconds
            leaves (List[Leaf]): list of leaves. Each leaf should have values: Dict attribute.
            workdir (str, optional): directory to save measurements. Defaults to "/tmp/xerxes".
        """
        self._period = period
        self._leaves = leaves
        self._workdir = workdir
        self._name = name
        log.info(f"Worker setup with period {period} and {len(leaves)} leaves")

    def start(self):
        """Start worker thread."""
        self._active = True
        super().start()

    def run(self):
        """Run worker thread.

        Periodically call job on leaves."""
        while self._period and self._active:
            log.debug(f"Starting job")
            self.job = Job(
                self._leaves, workdir=self._workdir, name=self._name
            )
            self.job.start()
            time.sleep(self._period)
            if self.job.is_alive():
                log.warning(f"Job {self.job} is still running")
            self.job.join()

    def stop(self):
        """Stop worker thread and join - wait for it to finish."""
        self._active = False
        self.job.join()
