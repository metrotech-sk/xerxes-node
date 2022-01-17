from pymongo import MongoClient

class DB:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://node:prokopcakovamama@xerxes.57jmr.mongodb.net/alfa?retryWrites=true&w=majority")