from pandas_datareader.famafrench import get_available_datasets
import pandas_datareader.data as web
import datetime
import seaborn as sns
from finlib import date_back

ds = web.DataReader('5_Industry_Portfolios', 'famafrench')

cap = ds[0]
eq = ds[0]
desc = ds['DESCR']
print(desc)
print(data)