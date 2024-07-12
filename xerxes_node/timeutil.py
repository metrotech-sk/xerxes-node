#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict
import time
import datetime


def add_timestamp(data: Dict) -> None:
    """Add timestamp to data dict."""

    data.update(
        {
            "time": {
                "epoch": time.time(),
                "datetime": datetime.datetime.now().isoformat(
                    timespec="seconds"
                ),
            }
        }
    )
