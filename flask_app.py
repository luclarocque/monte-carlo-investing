
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
# from flask_sqlalchemy import SQLAlchemy  # use this if database required
from montecarlo import simulate
import os, re
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(THIS_FOLDER, 'assets/images/')

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=["GET", "POST"])
def index():
    plot = ""
    errors = ""

    for fname in os.listdir(out_dir): # delete previously generated plot images
        path = out_dir + fname
        os.remove(path)

    if request.method == "GET":
        return render_template("display_plot.html")

    if request.method == "POST":
        pv = None
        pmt = None
        t = None
        r = None
        sd = None
        inflation = 0

        # validate input
        try:
            pv = float(request.form["pv"])
        except:
            errors += "PV {} is invalid.\n".format(request.form["pv"])
        try:
            pmt = float(request.form["pmt"])
        except:
            errors += "Payment {} is invalid.\n".format(request.form["pmt"])
        try:
            t = int(request.form["t"])
            if t <= 0:
                errors += "# years must be greater than 0.\n"
        except:
            errors += "# years {} is not a whole number.\n".format(request.form["t"])
        # try:
        #     r = float(request.form["r"])
        #     if r < 0:
        #         errors += "Annual interest rate must be greater than or equal to 0.\n"
        # except:
        #     errors += "Annual interest rate {} is invalid.\n".format(request.form["t"])

        # if errors occurred
        if errors:
            return render_template("display_plot.html", errors=errors)

        # variables defined. Apply simulate().
        interest = request.form["interest"]
        inflation = request.form.get('inflation')
        inflation = float(inflation) if inflation else 0
        print("inflation:", inflation)
        r, sd = map(float, str(interest).split(','))  # split string value obtained from radio button
        r -= inflation
        median, plot_fname = simulate(pv, pmt, t, r, sd)
        plot = "/static/images/{}".format(plot_fname)
        return render_template("display_plot.html", plot=plot)
        # return redirect(url_for('index'))




