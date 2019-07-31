# Date module
import datetime
import numpy as np
from scipy.optimize import fsolve
import pprint
pp = pprint.PrettyPrinter(indent=4)


def create_rand_array(r, sd, t, N, peryear=12):
    '''
    Creates an array of size (N, years*peryear) of N simulated runs.
    Elems are generated from a normal distribution with mean r and stddev sd.
    Each elem represents the amount of growth experienced in that period.
    e.g., 0.03 represents positive growth of 3%.

    Inputs:
    r: average annual ROR as percentage (e.g., use t=6 to represent 6%)
    sd: standard deviation as percentage (e.g., use t=10 to represent 10%)
    t: number of years
    N: number of simulations
    peryear: number of times deposits/withdrawals are made per year
    '''
    n = t*peryear
    return np.random.normal(r/100.,sd/100., (N, n)) / peryear


def FV(pv, pmt, t, r, peryear=12):
    '''
    Returns the future value of the annuity, compounded 'peryear' times
    per year over t years.

    Inputs:
    pv: present value
    pmt: amount of each payment, made 'peryear' times per year
    t: number of years
    r: annual rate of return percentage (e.g, r=7 for 7%)
    peryear: number of payments per year
    '''
    n = t*peryear
    r = r/peryear/100
    fv_principal = pv*(1+r)**n
    fv_pmts = pmt/r * ((1+r)**n - 1)
    return fv_principal + fv_pmts


def ror_with_pmts(fv, pv, pmt, t, peryear=12):
    '''
    Returns the compound annual growth rate of an investment with regular payments.
    Inputs:
    FV: future value
    pmt: non-zero regular payment amount.
    t: number of years
    peryear: number of payments per year
    '''
    def func(r):
        n = t*peryear
        r = r/peryear
        return pmt/r*((1+r)**n - 1) + pv*(1+r)**n - fv
    return float(fsolve(func, 0.07))


def recession_adjustment(arr, t, r, mean_drop=-30., std_drop=7., mean_duration=0.9, std_duration=0.3, mean_bull=5., std_bull=1.5):
    '''
    Returns an adjusted array based on arr of shape (N x num_months), where N: num_simulations. arr is over t years. 
    A recession lasts on average mean_duration years with a normally distributed drop.
    In between recessions are bull markets lasting on average mean_bull years.
    NOTE: recession_adjustment(arr, t, r) also mutates arr in-place
    All values are measured in years.
    '''
    N = arr.shape[0]  # number of simulations
    n = t*12  # total number of months
    for i in range(N):
        months_to_go = n
        while months_to_go > 0:
            if months_to_go == n:  # first run: shorten initial bull market
                bull_months = int(np.round(np.abs(np.random.normal(mean_bull/2, std_bull)*12)))
            else:
                bull_months = int(np.round(np.abs(np.random.normal(mean_bull, std_bull)*12)))
            months_to_go -= bull_months
            if months_to_go > 0:
                bear_months = int(np.round(np.abs(np.random.normal(mean_duration, std_duration)*12)))
                if months_to_go - bear_months <= 0:
                    break
                # print("mean annual growth initially:", np.mean(arr[i])*12)
                # print("bear market starts month", n - months_to_go)
                # print("bear_months:", bear_months)
                # pp.pprint(arr[i][-months_to_go:-(months_to_go-bear_months)])
                arr[i][-months_to_go:-(months_to_go-bear_months)] = np.random.normal(mean_drop/100., std_drop/100., bear_months)/12
                mean_i = np.mean(arr[i])
                # print("mean annual growth with recession:", mean_i*12)
                arr[i] = arr[i] + (np.random.normal(r/12/100, 0.01/12) - mean_i)
                # print("mean annual growth with mean adjusted up:", np.mean(arr[i])*12)
                # pp.pprint(arr[i][-months_to_go:-(months_to_go-bear_months)])
                months_to_go -= bear_months
    return arr


def date_back(curdate, years, months):
    '''
    curdate is a datetime.date object, years and months are the number
    of years and months to go back, respectively.
    '''
    extra_years = months // 12
    extra_months = months % 12
    m = (curdate.month - extra_months) % 12
    if m == 0:
        m = 12
    if m > curdate.month:
        extra_years += 1
    y = curdate.year - years - extra_years
    d = curdate.day
    if m == 2 and d > 28:
        d = 28
    elif m in [4,6,9,11] and d > 30:
        d = 30
    return datetime.date(y,m,d)


if __name__ == '__main__':

    # date = datetime.date(year=2019, month=7, day=1)
    # print(date_back(date, 0, 1))
    # print(date - datetime.timedelta(days=30))

    # --- Testing recession_adjustment ---
    # r = 7
    # sd = 11
    # years = 7
    # N = 1
    # arr = create_rand_array(r, sd, years, N)
    # recession_adjustment(arr, years, r)

    # --- Testing ror_with_pmts ---
    # ror = ror_with_pmts(873286.87, 30000, 3000, 15)
    # print(ror, ror/12)

    pass