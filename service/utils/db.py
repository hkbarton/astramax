from .env import *
import databases
import os


class Database:
    database = databases.Database(os.getenv("MAINDB_ADDR"))

    @classmethod
    def get_db(cls):
        return cls.database
