import pandas as pd
import pandas_datareader.data as web
import requests_cache
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

# the following 2 lines stop warnings
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# setup datareader and caching to store data from web
expire_after = datetime.timedelta(days=7)
session = requests_cache.CachedSession(cache_name='cache', backend='sqlite', expire_after=expire_after)
ds = web.DataReader('5_Industry_Portfolios', 'famafrench', session=session)

# See what data is found in this datareader dataset
# desc = ds['DESCR']
# print(desc)

# define dataframes to work with
dfCap = ds[0]
dfCap = dfCap.to_timestamp()
# print(dfCap.info())
# print(dfCap.head())

dfEq = ds[1]
dfEq = dfEq.to_timestamp()



# STATS
# quick stats
print("Cap-weighted:")
print(dfCap.describe())
print("\nEqual-weighted")
print(dfEq.describe())

# Kruskal Wallis (difference in medians?)
colsCap = [dfCap[col] for col in dfCap.columns]
colsEq = [dfEq[col] for col in dfCap.columns]

print("---Kruskal Wallis H-test---")
HCap, pvalCap = stats.kruskal(*colsCap)
HEq, pvalEq = stats.kruskal(*colsEq)
print("H-statistic:", HCap)
print("P-Value:", pvalCap)
print("H-statistic:", HEq)
print("P-Value:", pvalEq)

# T test
for colCap, colEq, ind in zip(colsCap, colsEq, range(dfCap.shape[1])):
    t, pval = stats.ttest_ind(colCap, colEq)
    print("\nSector: {}".format(dfCap.columns[ind]))
    print("t-stat:", t)
    print("P-Value:", pval)


# FIGURES
f1, (f1ax1, f1ax2) = plt.subplots(2, 1, figsize=(12,10))
sns.lineplot(data=dfCap, ax=f1ax1)\
    .set(ylim=(-30,30))
sns.lineplot(data=dfEq, ax=f1ax2)\
    .set(ylim=(-30,30))

plt.figure(figsize=(10,10))
sns.pairplot(data=dfCap)\
    .set(xlim=(-30,30), ylim=(-30,30))

plt.figure(figsize=(10,10))
sns.pairplot(data=dfEq)\
    .set(xlim=(-30,30), ylim=(-30,30))

f4, (f4ax1, f4ax2) = plt.subplots(2, 1, figsize=(8,12))
sns.catplot(data=dfCap, kind="violin", orient='h', ax=f4ax1)
sns.catplot(data=dfEq, kind="violin", orient='h', ax=f4ax2)
f4ax1.set(xlim=(-32, 32))
f4ax2.set(xlim=(-32, 32))

plt.show()