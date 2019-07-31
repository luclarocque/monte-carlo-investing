
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template
from montecarlo import simulate

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def index():
    return render_template("main_page.html")

