# Monte Carlo investing simulation
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from scipy.stats import percentileofscore
from finlib import create_rand_array, recession_adjustment, ror_with_pmts


def simulate(PV, PMT, t, r, sd, N=1000, peryear=12):
    '''
    Runs monte carlo simulation to determine possible investing/withdrawing outcomes

    Inputs:
    PV: present value (initial deposit)
    PMT: amount of regular deposit (or withdrawal if negative)
    t: number of years
    r: average annual ROR as percentage (e.g., use t=6 to represent 6%)
    sd: standard deviation as percentage (e.g., use t=10 to represent 10%)
    N: number of simulations
    peryear: number of times deposits/withdrawals are made per year
    '''
    n = t*peryear

    # percentiles to be displayed
    show_percentiles = [1,10,25,50,75,90,99]

    inc = 50000  # increment (step size) and bin width
    lb = int(-1e6)  # lower bound of bins
    ub = int(1e8)  # upper bound of bins
    bins = [[(k,k+inc-1),0] for k in range(lb,ub,inc)]

    # create random array: each row is a full simulation, with data for all years specified
    rand_arr = create_rand_array(r, sd, t, N, peryear)
    recession_adjustment(rand_arr, t, r)
    res_arr = []  # stores all final results
    for i in range(N):  # loop through N simulations
        res = PV
        for j in range(t*peryear):  # loop through all periods in a given simulation
            res = res*(1+rand_arr[i][j]) + PMT
            rand_arr[i][j] = res  # update amount at end of period
        res_bin = int(res // inc) - (lb // inc)  # determine index of bin this res belongs to
        res_arr.append(res)
        bins[res_bin][1] += 1  # increase count for the appropriate bin

    res_arr = np.array(res_arr)
    percentiles = np.percentile(res_arr, range(101), interpolation='lower')  # create array of percentiles to pull from
    # Print summary
    print("Based on {} simulations of {} years".format(N, t))
    print("PV:", PV, ",", "Payments:", PMT)
    # Warning for negative results
    if percentiles[0] < 0:
        print("*** Warning **********************")
        pct_low = len([i for i in res_arr if i < 0])/len(res_arr)*100
        print("{0:.2f}% of results are negative".format(pct_low))
        # Redo with different PMT if dipping too low: require <1% of results to be negative
        if percentiles[1] < 0:
            print("PMT changed to", PMT+100)
            PMT += 100
            return simulate(PV, PMT, t, r, sd, N=N, peryear=peryear)
    for p in show_percentiles:
        print("{}% chance of ending with more than ${:,.0f}".format(100-p, int(percentiles[p])))
    print("---"*10)
    break_even = PV+PMT*n
    if PMT > 0:
        print("Probability of breaking even with more than ${:,.0f}: {:,.1f}%".format(break_even, 100-percentileofscore(res_arr, break_even)))
    print("Probability of getting more than ${:,.0f}: {:,.1f}%".format(1e6, 100-percentileofscore(res_arr, 1e6)))


    # set up graph window
    fig = plt.figure(figsize=(16,9))
    gs = gridspec.GridSpec(2,2)
    ax1 = fig.add_subplot(gs[0,0]) # row 0, column 0

    # plot 1 (histogram) -------------------------------------------------
    ax1.title.set_text("Starting with ${:,.0f} over {} years with payments of {:,.0f}".format(PV, t, PMT))
    ax1.text(percentiles[50]-0.05*percentiles[50], 3, "50%:\n{:,}".format(int(percentiles[50])))
    ax1.axvline(x=percentiles[50], color='k')  # plot median line
    ax1.text(percentiles[5]-0.05*percentiles[5], 3, "5%:\n{:,}".format(int(percentiles[5])))
    ax1.axvline(x=percentiles[5], color='k')  # plot 5th percentile line

    # trimbins = trim_bins(bins)  # remove extraneous bins from both ends
    # plt_bins = np.array([b[0][0] for b in trimbins] + [trimbins[-1][0][1]])  # array of left endpoints + final right endpoint
    counts1, bins1, patches1 = ax1.hist(res_arr)

    # counts1, bins1, patches1 = ax1.hist(res_arr, plt_bins)
    # # colour the bars
    # num_bins = len(plt_bins)
    num_patches = len(patches1)
    for patch, i in zip(patches1, range(1, num_patches+1)):
        patch.set_facecolor( (0.3, 0.8*(i/num_patches), 0.8*(i/num_patches)) ) # (r,g,b)

    ax1.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))


    # plot 2 (percentiles) -------------------------------------------------
    ax2 = fig.add_subplot(gs[1, :]) # row 0, column 0

    num_bins = 25
    # step = (plt_bins[-1]-plt_bins[0])/num_bins

    counts2, bins2, patches2 = ax2.hist(res_arr, bins=num_bins, cumulative=-1, density=True)

    ax2.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    # if max(res_arr) > 100000:
    #     plt.xticks(np.arange((min(res_arr)//100000)*100000, (max(res_arr)//100000)*100000, percentiles[98]//500000*50000))

    plt.yticks([i for i in np.arange(0,1.1,0.1)])
    plt.grid(axis='y')

    # colour the bars
    num_patches = len(patches2)
    for patch, i in zip(patches2, range(1, num_patches+1)):
        patch.set_facecolor( (0.3, 0.8*(i/num_patches), 0.8*(i/num_patches)) ) # (r,g,b)

    # Label the percentiles above each bin
    for i, x in zip(range(num_bins), bins2[:-1]):
        percent = '{:.0f}%'.format(counts2[i]*100)
        # xytext: set location of text to display
        ax2.annotate(percent, xy=(x, 0), xytext=(x+bins2[0]*0.01,counts2[i]))


    # plot 3 (timeseries) -----------------
    ax3 = fig.add_subplot(gs[0,1]) # row 1 (second), span all columns

    # find the timeseries representing certain percentiles
    inds = [np.where(np.isclose(res_arr, percentiles[i]))[0][0] for i in show_percentiles]

    # plot timeseries
    timeseries = ax3.plot(rand_arr[inds].T)
    # annotate
    for i in range(len(inds)):
        fv = res_arr[inds[i]]
        cagr = ror_with_pmts(fv, PV, PMT, t, peryear=12)
        ax3.annotate("${:,.0f} | CAGR {:.1f}%".format(fv, cagr*100), xy=(n, fv), xytext=(n, fv))

    # legend
    labels = map(lambda x: str(100-x)+'%'+' chance', show_percentiles)
    ax3.legend(timeseries, labels)


    # final step---------------------------------------------------------
    plt.plot()
    return percentiles[50]



if __name__ == "__main__":
    ### Deposit stage ###
    # PV = 30000
    # PMT = 3000
    # years = 12
    # ROR = 7-1.8
    # sd = 11.4
    # simulate(PV, PMT, years, ROR, sd, N=2000)

    ### Daily habit
    # PV = 0
    # PMT = 2.30*21
    # years = 10
    # ROR = 6-1.8
    # sd = 11.4
    # simulate(PV, PMT, years, ROR, sd)

    ### Withdraw stage ###
    PV = 800000
    PMT = -2800
    years = 30
    ROR = 7-1.8
    sd = 11.4
    simulate(PV, PMT, years, ROR, sd)

    plt.show()
    # pass
