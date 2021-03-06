from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import pandas.plotting._converter as pandacnv
pandacnv.register()
from finlib import date_back, relative_return

tickers = ['VUN.TO', 'XIC.TO', 'XEC.TO']
num_years_back = 3
num_months_back = 0

'''
plot_stocks generates a plot of the growth of stocks specified
    in the tickers array.
Example input:
tickers = ['XUU.TO', 'XEF.TO', 'XEC.TO', 'HXT.TO']
num_years_back = 4
num_months_back = 0
'''
def plot_stocks(tickers, num_years_back=1, num_months_back=0):
    # get current date and time
    now = datetime.date.today()
    past = date_back(now, num_years_back, num_months_back)

    start_date = '{}-{}-{}'.format(past.year, past.month, past.day)
    end_date = '{}-{}-{}'.format(now.year, now.month, now.day)

    # User pandas_datareader.data.DataReader to load the desired data.
    panel_data = pdr.get_data_yahoo(tickers, start_date, end_date)
    close = panel_data['Close']
    close = close.fillna(method='ffill')
    print(close)


    # Plot everything by leveraging the very powerful matplotlib package
    fig, ax = plt.subplots(figsize=(16,9))

    for name in tickers:
        data = close.loc[:, name]
        stock_returns = relative_return(data)

        # Calculate the n_mav days moving averages of the closing prices
        n_mav = 60
        rolling_stock = stock_returns.rolling(window=n_mav, center=True)
        print()
        print(rolling_stock)
        rolling_stock_mean = rolling_stock.mean()
        ax.plot(stock_returns.index, stock_returns, label=name)
        ax.plot(rolling_stock_mean.index, rolling_stock_mean, label='{} : {} days rolling'.format(name, n_mav))

    ax.set_xlabel('Date')
    ax.set_ylabel('Percent change from start date (%)')
    ax.legend() 
    plt.grid(axis='y')
    plt.show()



if __name__ == '__main__':
    plot_stocks(tickers, num_years_back, num_months_back)



