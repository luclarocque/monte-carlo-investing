
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
# from flask_sqlalchemy import SQLAlchemy  # use this if database required
from montecarlo import simulate

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=["GET", "POST"])
def index():
    result = None
    errors = ""
    if request.method == "POST":
        pv = None
        pmt = None
        t = None
        r = None
        sd = 11.4
        try:
            pv = float(request.form["pv"])
            if pv == None:
                errors += "<p>You must fill enter a number in all fields.</p>\n"
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form["pv"])
        try:
            pmt = float(request.form["pmt"])
            if pmt == None:
                errors += "<p>You must fill enter a number in all fields.</p>\n"
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form["pmt"])
        try:
            t = int(request.form["t"])
            if t <= 0:
                errors += "<p>{!r} must be greater than 0.</p>\n".format(request.form["t"])
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form["t"])
        try:
            r = float(request.form["r"])
            if r < 0:
                errors += "<p>{!r} must be greater than or equal to 0.</p>\n".format(request.form["r"])
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form["t"])

        # if errors occurred
        if errors != "":
            return redirect(url_for('index'))

        # variables defined. Apply simulate().
        result = simulate(pv, pmt, t, r, sd)
        return render_template("monte_carlo.html", errors=errors, result=result)

    if request.method == "GET":
        return render_template("monte_carlo.html", errors=errors, result=result)



