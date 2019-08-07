
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
    result = ""
    plot = ""
    errors = ""

    for fname in os.listdir(out_dir): # delete previously generated plot images
        path = out_dir + fname
        os.remove(path)

    if request.method == "GET":
        return render_template("monte_carlo.html")

    if request.method == "POST":
        pv = None
        pmt = None
        t = None
        r = None
        sd = 11.4

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
        try:
            r = float(request.form["r"])
            if r < 0:
                errors += "Annual interest rate must be greater than or equal to 0.\n"
        except:
            errors += "Annual interest rate {} is invalid.\n".format(request.form["t"])

        # if errors occurred
        if errors:
            return render_template("monte_carlo.html", errors=errors)
            # return redirect(url_for('index'))

        # variables defined. Apply simulate().
        result, plot_fname = simulate(pv, pmt, t, r, sd)
        result = '''
        <div class="row">
        ''' + \
        '''
            The median outcome upon running 2,000 possible random scenarios is: {}
        '''.format(result) + \
        '''
        </div>
        '''
        plot = '''
            <div>
                <style scoped>
                    img {
                          max-width: 110%;
                          height: auto;
                        }
                </style>
            ''' + \
            '    <img src=/static/images/{} alt="Plots of simulation results">'.format(plot_fname) + \
            '''
            </div>
            '''
        return render_template("monte_carlo.html", result=result, plot=plot)




