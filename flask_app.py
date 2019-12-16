
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
# from flask_sqlalchemy import SQLAlchemy  # use this if database required
from montecarlo import simulate
import os
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
        N = None
        inflation = 0

        # define dictionary of values: (interest, stddev). Key is percentage in equities.
        interest_sd_dict = {'100': (6.6, 10.6),
                            '80': (5.9, 8.7),
                            '60': (5.2, 6.8),
                            '40': (4.6, 5.3),
                            '20': (3.9, 4.1),
                            '0': (3.2, 3.9)}

        # validate input ----------------------------------------------------------------------------
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
        try:
            asset_mix = request.form['asset_mix']
        except:
            errors += "You must select an asset mix to determine the expected annual rate of return."
        try:
            N = int(request.form["num_sims"])
        except:
            errors += "You must select the number of simulations to run."
        # if errors occurred
        if errors:
            return render_template("error.html", errors=errors)
        # -------------------------------------------------------------------------------------------

        # define variables and simulate
        inflation = request.form.get('inflation')
        inflation = float(inflation) if inflation else 0
        r, sd = interest_sd_dict[asset_mix]  # get value from radio button to extract r, sd
        r -= inflation
        median, plot_fname = simulate(pv, pmt, t, r, sd, N=N)
        plot = "/static/images/{}".format(plot_fname)

        return render_template("display_plot.html", plot=plot)
        # return redirect(url_for('index'))




