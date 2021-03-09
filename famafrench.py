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
# print(dfEq.info())
# print(dfEq.head())


# STATS
# quick stats
print("Cap-weighted:")
print(dfCap.describe())
print("\nEqual-weighted")
print(dfEq.describe())

# Kruskal Wallis (difference in medians?)
colsCap = [dfCap[col] for col in dfCap.columns]
colsEq = [dfEq[col] for col in dfCap.columns]

print("***Kruskal Wallis H-test (can we conclude that the medians differ?)")
HCap, pvalCap = stats.kruskal(*colsCap)
HEq, pvalEq = stats.kruskal(*colsEq)
print("Cap-weighted:")
print("H-statistic:", HCap)
print("P-Value:", pvalCap)
print("\nEqual-weighted:")
print("H-statistic:", HEq)
print("P-Value:", pvalEq)

# T test (compare the means of Cap vs. Equal-weighted sector by sector)
# Use Welch's -- unequal variances
for colCap, colEq, ind in zip(colsCap, colsEq, range(dfCap.shape[1])):
    t, pval = stats.ttest_ind(colCap, colEq, equal_var=False)
    print("\n{}".format(dfCap.columns[ind]))
    print("t-stat:", t)
    print("P-Value:", pval)


# FIGURES
# line graphs
f1, (f1ax1, f1ax2) = plt.subplots(2, 1, figsize=(12,10))
sns.lineplot(data=dfCap, ax=f1ax1).set(ylim=(-30,30))
f1ax1.title.set_text('Cap-weighted Portfolios')

sns.lineplot(data=dfEq, ax=f1ax2).set(ylim=(-30,30))
f1ax2.title.set_text('Equal-weighted Portfolios')

# pair plots (scatterplot + histogram [diagonal entries])
plt.figure(figsize=(10,10))
sns.pairplot(data=dfCap).set(xlim=(-30,30), ylim=(-30,30))
plt.gcf().suptitle('Cap-weighted Portfolios', y=1)

plt.figure(figsize=(10,10))
sns.pairplot(data=dfEq).set(xlim=(-30,30), ylim=(-30,30))
plt.gcf().suptitle('Equal-weighted Portfolios', y=1)

# violin plots
f4, (f4ax1, f4ax2) = plt.subplots(2, 1, figsize=(8,12))
sns.catplot(data=dfCap, kind="violin", orient='h', ax=f4ax1)
f4ax1.title.set_text('Cap-weighted Portfolios')
f4ax1.set(xlim=(-32, 32))

sns.catplot(data=dfEq, kind="violin", orient='h', ax=f4ax2)
f4ax2.title.set_text('Equal-weighted Portfolios')
f4ax2.set(xlim=(-32, 32))

plt.show()