# Monte Carlo investing simulation
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from matplotlib.ticker import AutoMinorLocator
import seaborn as sns
from scipy.stats import percentileofscore
from finlib import create_rand_array, recession_adjustment, ror_with_pmts, short_num
import os

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
fileid = np.random.randint(1e9, 9e9, dtype='int64')
plot_fname = 'plot{}.png'.format(fileid)
out_filename = os.path.join(THIS_FOLDER, 'assets/images/' + plot_fname)


def simulate(PV, PMT, t, r, sd, N=1000, peryear=12, show_percentiles=(90, 75, 50, 25, 5, 1), allow_drawdown=True):
    """
    Runs monte carlo simulation to determine possible investing/withdrawing outcomes

    Inputs:
    PV: present value (initial deposit)
    PMT: amount of regular deposit (or withdrawal if negative)
    t: number of years
    r: average annual ROR as percentage (e.g., use t=6 to represent 6%)
    sd: standard deviation as percentage (e.g., use t=10 to represent 10%)
    N: number of simulations
    peryear: number of times deposits/withdrawals are made per year
    """
    n = t * peryear

    inc = 50000  # increment (step size) and bin width
    lb = int(-1e6)  # lower bound of bins
    ub = int(1e8)  # upper bound of bins
    bins = [[(k, k + inc - 1), 0] for k in range(lb, ub, inc)]

    # create random array: each row is a full simulation, with data for all years specified
    rand_arr = create_rand_array(r, sd, t, N, peryear)
    recession_adjustment(rand_arr, t, r)
    res_arr = []  # stores all final results (all data stored here)
    for i in range(N):  # loop through N simulations
        res = PV
        for j in range(t * peryear):  # loop through all periods in a given simulation
            res = res * (1 + rand_arr[i][j]) + PMT
            rand_arr[i][j] = res  # update amount at end of period
        res_bin = int(res // inc) - (lb // inc)  # determine index of bin this res belongs to
        res_arr.append(res)
        bins[res_bin][1] += 1  # increase count for the appropriate bin

    res_arr = np.array(res_arr)
    percentiles = np.percentile(res_arr, range(101), interpolation='lower')  # create array of percentiles to pull from
    # Print summary
    print("Based on {} simulations of {} years".format(N, t))
    print("PV:", PV, ",", "Payments:", PMT)
    # Warning for negative results (drawdown)
    if percentiles[0] < 0:
        print("*** Warning **********************")
        pct_low = len([i for i in res_arr if i < 0]) / len(res_arr) * 100
        print("{0:.2f}% of results are negative".format(pct_low))
        if not allow_drawdown:
            # Redo with different PMT if dipping below 0
            print("PMT changed to", PMT + 100)
            PMT += 100
            return simulate(PV, PMT, t, r, sd, N=N, peryear=peryear)
    for p in show_percentiles:
        print("{}% chance of ending with more than ${:,.0f}".format(100 - p, int(percentiles[p])))
    print("---" * 10)
    break_even = PV + PMT * n
    if PMT < 0:
        break_even = PV
    print("Probability of breaking even with more than ${:,.0f}: {:,.1f}%".format(break_even,
                                                                                  100 - percentileofscore(res_arr,
                                                                                                          break_even)))
    print("Probability of getting more than ${:,.0f}: {:,.1f}%".format(1e6, 100 - percentileofscore(res_arr, 1e6)))

    # set up graph window
    fig = plt.figure(figsize=(16, 9))
    gs = gridspec.GridSpec(2, 3)

    # plot 1 (histogram) -------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])  # row 0, column 0

    # plot histogram
    counts1, bins1, patches1 = ax1.hist(res_arr)

    # add vertical line indicating the median
    ax1.text(percentiles[50], 3, "50%:\n{:,}".format(int(percentiles[50])), color='w')
    ax1.axvline(x=percentiles[50], color='k')  # plot median line

    # formatting
    ax1.title.set_text(
        "Starting with \${:,.0f} with {:,.1f}% interest over {} years and payments of \${:,.0f}".format(PV, r, t, PMT))
    ax1.xaxis.set_label_text("Total Market Value")
    ax1.yaxis.set_label_text("Number of Simulations (out of {})".format(N))
    ax1.xaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda long_num, b: format(short_num(long_num))))
    ax1.xaxis.set_minor_locator(AutoMinorLocator())

    # colour the bars
    num_patches = len(patches1)
    tot_counts1 = sum(counts1)
    for patch, i in zip(patches1, range(0, num_patches)):
        patch.set_facecolor((
            max(1 - 2.2 * counts1[i] / tot_counts1, 0),
            min(1.2 * np.sqrt(counts1[i] / tot_counts1), 1),
            min(1.1 * np.sqrt(counts1[i] / tot_counts1), 1)))

    # plot 2 (percentiles) -------------------------------------------------
    ax2 = fig.add_subplot(gs[1, 0:2])  # row 1 (second), span first 2 columns
    num_bins = 24

    # plot histogram
    counts2, bins2, patches2 = ax2.hist(res_arr, bins=num_bins, cumulative=-1, density=True)

    # formatting
    ax2.title.set_text("(Reverse) Cumulative Probability of Results")
    ax2.xaxis.set_label_text("Total Market Value")
    ax2.yaxis.set_label_text("Probability of Getting AT LEAST...")
    ax2.xaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, p: format(short_num(x))))
    ax2.xaxis.set_minor_locator(AutoMinorLocator())
    plt.yticks([i for i in np.arange(0, 1.1, 0.1)],
               [str(i) + '%' for i in np.arange(0, 110, 10)])
    plt.grid(axis='y')

    # colour the bars
    num_patches = len(patches2)
    tot_counts2 = sum(counts2)
    for patch, i in zip(patches2, range(0, num_patches)):
        patch.set_facecolor((
            min(2 * counts2[i] / tot_counts2, 1),
            max(1 - 3 * np.sqrt(counts2[i] / tot_counts2), 0),
            max(1 - 2 * np.sqrt(counts2[i] / tot_counts2), 0)))

    # Label the percentiles above each bin
    for i, x in zip(range(num_bins), bins2[:-1]):
        percent = '{:.0f}%'.format(counts2[i] * 100)
        # xytext: set location of text to display
        ax2.annotate(percent, xy=(x, 0), xytext=(x + bins2[0] * 0.01, counts2[i]))

    # plot 3 (timeseries) --------------------------------------------------
    ax3 = fig.add_subplot(gs[0, 1:3])  # row 0, column 1 and 2

    # find the timeseries representing certain percentiles
    inds = [np.where(np.isclose(res_arr, percentiles[i]))[0][0] for i in show_percentiles]

    # plot timeseries
    timeseries = ax3.plot(rand_arr[inds].T)

    # formatting
    ax3.title.set_text("Timeseries of Specified Percentiles")
    ax3.xaxis.set_label_text("Month")
    ax3.yaxis.set_label_text("Total Market Value")
    ax3.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda long_num, b: format(short_num(long_num))))
    xticks, _ = plt.xticks()  # array of xtick locations (values on axis)
    tick_diff = xticks[1] - xticks[0]
    outcome_str_lst = []  # store outcome strings to include in legend
    for i in range(len(inds)):
        fv = res_arr[inds[i]]
        cagr = ror_with_pmts(fv, PV, PMT, t, peryear=12)
        outcome_str_lst.append("${:,.0f} | CAGR {:.1f}%".format(fv, cagr * 100))
        # ax3.annotate("${:,.0f} | CAGR {:.1f}%".format(fv, cagr * 100), xy=(n + tick_diff / 8, fv),
        #              xytext=(n + tick_diff / 8, fv))

    # legend
    # show_percentiles.reverse()  # to display in proper order in legend of ax3
    labels = [str(pct) + 'th' + ' percentile: ' + out_str for pct, out_str in zip(show_percentiles, outcome_str_lst)]
    ax3.legend(timeseries, labels, loc='upper left')


    # boxplot -----------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 2])  # row 1, column 2
    sns.boxenplot(data=res_arr)
    ax4.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda long_num, b: format(short_num(long_num))))
    plt.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)  # labels along the bottom edge are off


    # final step---------------------------------------------------------
    # plt.plot()
    plt.savefig(out_filename)  # ***Uncomment plt.savefig for use with webapp
    return "${:,.2f}".format(percentiles[50]), plot_fname


if __name__ == "__main__":
    # -- Deposit stage -- #
    PV = 39000
    PMT = 4000
    years = 14
    ROR = 6.4
    sd = 10.6
    simulate(PV, PMT, years, ROR, sd, N=1000)

    # -- Daily habit -- #
    # PV = 0
    # PMT = 2.30*21
    # years = 10
    # ROR = 6-1.8
    # sd = 11.4
    # simulate(PV, PMT, years, ROR, sd)

    # -- Withdraw stage -- #
    # PV = 800000
    # PMT = -2500
    # years = 60
    # ROR = 4.9
    # sd = 9.5
    # simulate(PV, PMT, years, ROR, sd, show_percentiles=[0,1,5,10,15,25], N=1000)

    plt.show()
