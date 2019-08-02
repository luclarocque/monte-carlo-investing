
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
# from flask_sqlalchemy import SQLAlchemy  # use this if database required
from montecarlo import simulate
import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
plot_filename = os.path.join(THIS_FOLDER, 'assets/images/plot.png')

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=["GET", "POST"])
def index():
    result = None
    plot = ""
    errors = ""
    if request.method == "POST":
        pv = None
        pmt = None
        t = None
        r = None
        sd = 11.4

        # validate input
        try:
            pv = float(request.form["pv"])
            if pv == None:
                errors += "You must enter a number in all fields.\n"
        except:
            errors += "{} is not a number.\n".format(request.form["pv"])
        try:
            pmt = float(request.form["pmt"])
            if pmt == None:
                errors += "You must enter a number in all fields.\n"
        except:
            errors += "{} is not a number.\n".format(request.form["pmt"])
        try:
            t = int(request.form["t"])
            if t <= 0:
                errors += "Number of years (t) must be greater than 0.\n".format(request.form["t"])
        except:
            errors += "{} is not a number.\n".format(request.form["t"])
        try:
            r = float(request.form["r"])
            if r < 0:
                errors += "Annual interest (I/Y) must be greater than or equal to 0.\n".format(request.form["r"])
        except:
            errors += "{} is not a number.\n".format(request.form["t"])

        # if errors occurred
        if errors != "":
            return render_template("monte_carlo.html", errors=errors)
            # return redirect(url_for('index'))

        # variables defined. Apply simulate().
        result = simulate(pv, pmt, t, r, sd)
        plot = plot_filename
        return render_template("monte_carlo.html", errors=errors, result=result, plot=plot)

    if request.method == "GET":
        if result == None:
            return render_template("monte_carlo.html", errors=errors)
        else:
            return render_template("monte_carlo.html", errors=errors, result=result, plot=plot)



