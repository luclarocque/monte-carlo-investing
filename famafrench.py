import pandas as pd
import pandas_datareader.data as web
import requests_cache
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

# the following 2 lines stop warnings
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# setup datareader and caching to store data from web
expire_after = datetime.timedelta(days=7)
session = requests_cache.CachedSession(cache_name='cache', backend='sqlite', expire_after=expire_after)
ds = web.DataReader('5_Industry_Portfolios', 'famafrench', session=session)

# See what data is found in this datareader dataset
# desc = ds['DESCR']

# define dataframes to work with
dfCap = ds[0]
dfCap = dfCap.to_timestamp()
# dfEq = ds[2]
# dfEq = dfEq.to_timestamp()

# print(dfCap.info())
# print(dfCap.head())
# print(dfCap.describe())

plt.figure()
sns.lineplot(data=dfCap)

# TODO: make same scale
plt.figure()
sns.pairplot(data=dfCap)

# boxplot
plt.figure()
sns.catplot(data=dfCap, kind="violin")


plt.show()