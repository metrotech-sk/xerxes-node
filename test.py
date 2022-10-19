#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def to_json(__o: object) -> str:
    assert isinstance(__, object)
    for param in __o.__dir__:
        if not param.startswith("__")

class A:
    a = 5
    g = [1,2,3]
    d = {
        "b": "B"
    }
    def blah(self):
        pass

print(to_json(A()))