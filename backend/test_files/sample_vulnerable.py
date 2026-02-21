import os
import sys
import subprocess
import pickle
from flask import request
from sqlite3 import connect

SECRET_KEY = "super_secret"
DEBUG, VERSION = True, "1.0"
a, b = 1, 2
x = y = 5

db = connect("test.db")

class UserManager:
    def __init__(self, db):
        self.db = db

    def login(self):
        username = request.args.get("username")
        password = input("Enter password: ")
        query = f"SELECT * FROM users WHERE username = '{username}'"
        cursor = self.db.cursor()
        cursor.execute(query)

    def dangerous_method(self):
        cmd = request.form.get("cmd")
        os.system(cmd)

        data = request.json
        eval(data)

def standalone_function():
    arg = sys.argv[1]
    subprocess.run(arg)

    raw = input("Give me something:")
    pickle.loads(raw)

try:
    user_input = request.args.get("data")
    exec(user_input)
except Exception:
    pass