#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Eric Vansteenberghe
Quantitative Methods in Finance
Beginner exercise with pandas DataFrames - part 2
2020
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.tsa.stattools
import statsmodels.formula.api as smf
import scipy.stats

# to plot, set ploton to ploton to 1
ploton = False

# change the working directory
os.chdir('//Users/skimeur/Google Drive/empirical_finance/')

#%% Import the data on French population again as in part 1
# Import French population data
df = pd.read_csv('data/Valeurs.csv', sep=';', encoding='latin1', skiprows=[0,1,2], header=None, index_col=False)
df = df.iloc[::-1]
df.columns = ['Year','Month','Population']
df.index = pd.to_datetime((df.Year*100+df.Month).apply(str),format='%Y%m')
df = df.drop(['Year','Month'],1)
df = df.replace({' ': ''}, regex=True) 
df = df.astype(float)
df = df / 1000
df_change = 100 * (df/df.shift(1)-1)

#%% From the average monthly French population change, 
# we want to append to your DataFrame some projections until 2020, plot this projection.

# compute the average monthly change
avgchg = df_change.mean()[0]/100

# create a new df with index of dates we want
dates3 = pd.date_range('1994-01', '2020-01', freq='M') 
dfproj = pd.DataFrame(index=dates3)
dfproj = dfproj.join(df)

for i in range(0,len(dfproj)-1):
    if np.isnan(dfproj.iloc[i+1,0]):
        dfproj.iloc[i+1] = dfproj.iloc[i] * (1 + avgchg)

if ploton:
    ax = dfproj.plot(title='French population in million projected up to 2020')
    fig = ax.get_figure()
    #fig.savefig('frenchpopproj.pdf')

dfproj_change = (dfproj/dfproj.shift(1))-1
if ploton:
    dfproj_change.plot()

#%% Confidence interval

# we compute the standard error of the changes
df_change.std()[0]/100

# we first create a dfest with the estimated value if we take the avegchg
# we use copy, deep copy as we don't want dfest to be "linked" with df anymore
dfest = df.copy(deep=True)
for i in range(1,len(dfest)):
    dfest.iloc[i] = df.iloc[i-1]* (1 + avgchg)

dfcompare = pd.concat([df,dfest],axis=1)
if ploton:
    dfcompare.plot()
    dfest.plot()
    df.plot()

# we compute the error terms
errors = dfest - df

if ploton:
    errors.hist(bins=50)

# drop the first errors element as it was not an output of our projection
errors = errors.iloc[1:]

# check that the mean of our error should be around 0
errors.mean()

# we compute the standard error of the error term and take 5% confidence inteval
stde = errors.std()[0]
# this is the standard error with a forecast at horizon one

# discuss which standard error we should consider for the confidence interval

# normal two sided distribution
z = scipy.stats.norm.ppf(0.975)

if ploton:
    # we want to plot the normal distribution
    dx = 0.0001  # resolution
    x = np.arange(-0.1, 0.1, dx)
    # normal distribution
    pdf = scipy.stats.norm.pdf(x, errors.mean()[0], errors.std()[0])
    alpha = 0.025  # confidence level
    LeftThres = -scipy.stats.norm.ppf(1-alpha, errors.mean()[0], errors.std()[0])
    RightThres = scipy.stats.norm.ppf(1-alpha, errors.mean()[0], errors.std()[0])
    plt.figure(num=1, figsize=(11, 6))
    plt.plot(x, pdf, 'b', label="Normally distributed errors")
    #plt.hold(True)
    plt.axis("tight")
    # Vertical lines
    plt.plot([LeftThres, LeftThres], [0, 3.8], c='r')
    plt.plot([RightThres, RightThres], [0, 3.8], c='r')
    plt.xlim([-0.1, 0.1])
    plt.ylim([0, 26])
    plt.legend(loc="best")
    plt.xlabel("Errors")
    plt.ylabel("Probability of occurence")
    plt.title("Error distribution and confidence at 5%")
    #plt.show()
    plt.savefig('fig/errors_conf.png')

# if we take the value from the t distribution:
zbis = scipy.stats.t.ppf(0.975,len(errors)-1)

# norm.ppf is the inverse of the cumulative normal distribution function
x3 = np.arange(0,1,0.01)
y3 = scipy.stats.norm.ppf(x3)
# cumulative distribution function
x4 = np.arange(-2.5,2.5,0.01)
y4 = scipy.stats.norm.cdf(x4)
# note here that we plot x as a function of y, because it is the inverse!!!
if ploton:
    plt.plot(y3,x3)
    # we plot the cumulative distribution function
    plt.plot(x4,y4)
    # hence the function norm.ppf gives us the value z at which the cumulative probability is 97.5%

# we create the confidence interval
dfproj['CIplus']=np.NaN
dfproj['CIminus']=np.NaN

j = 1
for i in range(len(df),len(dfproj)):
    dfproj.iloc[i,1] = dfproj.iloc[i,0] + z * stde * (1 - avgchg**(2*j)) /  (1 - avgchg**2)
    dfproj.iloc[i,2] = dfproj.iloc[i,0] - z * stde * (1 - avgchg**(2*j)) /  (1 - avgchg**2)
    j += 1

if ploton:
    ax = dfproj.iloc[250:,:].plot(title='French population projection with an idea of confidence interval')
    fig = ax.get_figure()
    fig.savefig('fig/frenchpopCI.pdf')

# or second option
stdelist = []
# forecast at horizon t
for t in range(1,len(dfproj)-len(df)):
    dfest = df.copy(deep=True)
    for i in range(t,len(dfest)):
        dfest.iloc[i] = df.iloc[i-t] * ( (1 + avgchg)**t )
    # we compute the error terms
    errors = dfest - df
    # drop the first t errors element as it was not an output of our projection
    errors = errors.iloc[t:]
    # we compute the standard error of the error term and take 5% confidence inteval
    stdelist.append(errors.std()[0])

# we create the confidence interval
dfproj['CIplus']=np.NaN
dfproj['CIminus']=np.NaN

j = 0
for i in range(len(df),len(dfproj)-1):
    dfproj.iloc[i,1] = dfproj.iloc[i,0] + stdelist[j] * z
    dfproj.iloc[i,2] = dfproj.iloc[i,0] - stdelist[j] * z
    j += 1

if ploton:
    ax = dfproj.iloc[:,:].plot(title='French population projection with an idea of confidence interval')
    fig = ax.get_figure()
    #fig.savefig('frenchpopCI2.pdf')


#%% population: trend with an AR component?

# first diff
dfdiff = df - df.shift(1)
dfdiff = dfdiff.dropna()

# stationarity of our series
statsmodels.tsa.stattools.adfuller(df.unstack(), regression='ct')
statsmodels.tsa.stattools.adfuller(dfdiff.unstack(), regression='ct')
# it is I(1)

dfdiff['time'] = range(1,len(dfdiff)+1)
dfdiff['pop1'] = df.shift(1)

popols = smf.ols('Population ~ time +  pop1',data=dfdiff).fit()
popols.summary()

dfest = df.copy(deep=True)
for i in range(1,len(dfest)):
    dfest.iloc[i] = popols.params[0] + i * popols.params[1] + (1 + popols.params[2]) * dfest.iloc[i-1]

dfcompare = pd.concat([df,dfest],axis=1)
if ploton:
    dfcompare.plot()

# create a new df with index of dates we want
dates3 = pd.date_range('1994-01', '2020-01', freq='M') 
dfproj = pd.DataFrame(index=dates3)
dfproj = dfproj.join(df)

for i in range(0,len(dfproj)-1):
    if np.isnan(dfproj.iloc[i+1,0]):
        dfproj.iloc[i+1] = popols.params[0] + i * popols.params[1] + (1 + popols.params[2]) * dfproj.iloc[i]

stdeAR = (df - dfest).std()[0]

# or second option
stdelist = []
# forecast at horizon t
for t in range(1,len(dfproj)-len(df)):
    dfest = df.copy(deep=True)
    for i in range(t,len(dfest)):
        dfest.iloc[i] = popols.params[0] + i * popols.params[1] + (1 + popols.params[2]) * dfest.iloc[i-1]
    # we compute the error terms
    errors = dfest - df
    # drop the first t errors element as it was not an output of our projection
    errors = errors.iloc[t:]
    # we compute the standard error of the error term and take 5% confidence inteval
    stdelist.append(errors.std()[0])

# we create the confidence interval
dfproj['CIplus']=np.NaN
dfproj['CIminus']=np.NaN

j = 0
for i in range(len(df),len(dfproj)-1):
    dfproj.iloc[i,1] = dfproj.iloc[i,0] + stdelist[j] * z
    dfproj.iloc[i,2] = dfproj.iloc[i,0] - stdelist[j] * z
    j += 1

if ploton:
    ax = dfproj.iloc[:,:].plot(title='French population projection with an idea of confidence interval')
    fig = ax.get_figure()
    #fig.savefig('fig/frenchpopCI3.pdf')


#%% Augmenting our model with the error terms

dfest = df.copy(deep=True)
for i in range(1,len(dfest)):
    if i > 2:
        dfest.iloc[i] = popols.params[0] + i * popols.params[1] + (1 + popols.params[2]) * dfest.iloc[i-1] + df.iloc[i-1] - dfest.iloc[i-1]
    else:
        dfest.iloc[i] = popols.params[0] + i * popols.params[1] + (1 + popols.params[2]) * dfest.iloc[i-1]

dfcompare = pd.concat([df,dfest],axis=1)
#dfcompare.plot()

# we compute the error terms
errors = dfest - df

# we compute the standard error of the error term and take 5% confidence inteval
stdeaugm = errors.std()[0]

# or second option
stdelist = []
# forecast at horizon t
for t in range(1,len(dfproj)-len(df)):
    dfest = df.copy(deep=True)
    for i in range(t,len(dfest)):
        dfest.iloc[i] = df.iloc[i-t] * ( (1 + avgchg)**t )
    # we compute the error terms
    errors = dfest - df
    # drop the first t errors element as it was not an output of our projection
    errors = errors.iloc[t:]
    # we compute the standard error of the error term and take 5% confidence inteval
    stdelist.append(errors.std()[0])

# we create the confidence interval
dfproj['CIplus']=np.NaN
dfproj['CIminus']=np.NaN

j = 0
for i in range(len(df),len(dfproj)-1):
    dfproj.iloc[i,1] = dfproj.iloc[i,0] + stdelist[j] * z
    dfproj.iloc[i,2] = dfproj.iloc[i,0] - stdelist[j] * z
    j += 1

if ploton:
    ax = dfproj.iloc[:,:].plot(title='French population projection with an idea of confidence interval')
    fig = ax.get_figure()
    #fig.savefig('fig/frenchpopCIaugmented.pdf')

#%% Exercise: stick to the monthly seasonality, 
# compute a monthly average population change and use it to project the population up to 2020

del dfdiff, stdeaugm, stdeAR, stdelist, t, avgchg, stde, z, df_change, dfproj, dfproj_change, dates3, dfcompare, dfest, errors, i, j, x3, y3, x4, y4, zbis

    