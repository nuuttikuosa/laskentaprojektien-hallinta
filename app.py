import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
import config, users

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")