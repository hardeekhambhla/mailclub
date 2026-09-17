import os

DB_PATH = os.environ.get("MAILCLUB_DB_PATH", os.path.join(os.path.dirname(__file__), "mailclub.db"))
PORT = int(os.environ.get("MAILCLUB_PORT", "5757"))
