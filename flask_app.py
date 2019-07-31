
# A very simple Flask Hello World app for you to get started with...

from flask import Flask
from montecarlo import simulate

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def hello_world():
    return 'My first attempt at a webapp'

