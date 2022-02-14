#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 11:27:00 2022

@author: Eric Vansteenberghe
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pareto, genpareto, lognorm, weibull_min, expon
from scipy.stats import probplot # for Probability plots
import statsmodels.api as sm # for Q-Q plots

# To plot, set ploton to True
ploton = False

# We set the working directory (useful to chose the folder where to export output files)
os.chdir('/Users/skimeur/Google Drive/empirical_finance')

#%% Pareto distribution of claim sizes

# we chose 1 < alpha < 2
alphai = 1.95
xm = ((alphai-1)/alphai) * 1000

# illustration of the variance as n tends to infinity
Nplist = [10,5*10,10**2,5*10**2,10**3,5*10**3,10**4,10**5,10**6,10**7,10**8]
Varlist = []
Meanlist = []
for Npi in Nplist:
    pop = pareto.rvs(b=alphai, scale=xm, size=Npi)
    Varlist.append(np.std(pop))
    Meanlist.append(np.mean(pop))
    
if ploton:
    plt.loglog(Nplist,Varlist) # observe that Var(X) -> infinity
    plt.loglog(Nplist,Meanlist) # observe that indeed E(X) -> 1000

# probability density function
def pdfpareto(x,alphai,xm):
    return alphai * (xm**alphai)/(x**(alphai+1))

# plot the probability density
dx = 0.001  # resolution
x = np.arange(500, 10000, dx)
pdf = pareto.pdf(x, b=alphai, scale=xm)

if ploton:
    plt.plot(x, pdf, 'b', label="Pareto PDF")
    plt.xlabel("Variable value")
    plt.ylabel("Probability of occurence")
    plt.show()
    plt.close()

del alphai, dx, Meanlist, Npi, Nplist, pdf, pop, Varlist, x, xm

#%% Norwegian fire data

# Import the data set, we found it via ReIns package in R
df = pd.read_csv('data/norwegianfire.csv', index_col=0)

# convert years to year
df.year = pd.to_datetime(df.year, format="%y")

# we cannot really plot the time series as each observation is only per year
# instead for visual, we plot the max per year
if ploton:
    df.groupby('year')['size'].max().plot(x='year')

# what is our theshold u, it should be 500 Kronen
u = min(df['size'])

if ploton:
    df['size'].hist(bins=50, density=True, log=True)

#%% Q-Q plot
# normal law
if ploton:
    sm.qqplot(df['size'], line='r')

# exponential law
if ploton:
    sm.qqplot(df['size'], line='r', dist=expon)


# log-normal law
# you have to indicate the shape parameter in the distargs arguments
if ploton:
    shapelgn = lognorm.fit(df['size'])[0]
    sm.qqplot(df['size'], line='r', dist=lognorm, distargs=(shapelgn, ))

    
# Weibull law
# nota bene: in the sparams, you need to choose the shape parameter
if ploton:
    c = weibull_min.fit(df['size'])[0]
    sm.qqplot(np.log(df['size']), dist=weibull_min, distargs=(c, ), line='r')


# Pareto law
# nota bene: in the sparams, you need to define the scale parameter, here it is u=500 Kronen
if ploton:
    sm.qqplot(np.log(df['size']), dist=pareto, distargs=(u, ), line='r')
    # cf. Prboplot documentation
    probplot(np.log(df['size']), dist="pareto", plot=plt, sparams=(u, ))

# change u
percentilei = 95
uprime = np.percentile(df['size'], percentilei)

print("We keep only", np.round(100 * len(df.loc[df['size']>=uprime,'size'])/len(df)), "percent of observations")

# plot the updated histogram
if ploton:
    df.loc[df['size']>=uprime,'size'].hist(bins=50, density=True, log=True)

# Q-Q plot for a Pareto
if ploton:
    sm.qqplot(np.log(df.loc[df['size']>=uprime,'size']), dist=pareto, distargs=(uprime, ), line='r')
    # cf. Prboplot documentation
    probplot(np.log(df.loc[df['size']>=uprime,'size']), dist="pareto", plot=plt, sparams=(uprime, ))

#%% Pareto type 1
# estimate a Pareto distribution
print('Hill estimator', 1 / ( (1/len(df)) * np.sum(np.log(df['size'] / df['size'].min()))) )
# obviously, we get the same estimate with scipy's package

print('Scipy Pareto type I estimator', pareto.fit(df['size'], scale=u)[0])

# now if we change the threshold, the estimate of alhpa also changes
pareto.fit(df.loc[df['size']>=uprime,'size'])
print('Scipy Pareto type I estimator upper threshold', pareto.fit(df.loc[df['size']>=uprime,'size'])[0])

#%% Parto type 2

# in the definition of the way it is implemented in scipy we have:
# alpha = 1 / c
# u = loc
# sigma = scale
print('Scipy Pareto type II estimator', 1 / genpareto.fit(df['size'], loc=u)[0])

# now if we change the threshold, the estimate of alhpa also changes
print('Scipy Pareto type I estimator upper threshold', 1 / genpareto.fit(df.loc[df['size']>=uprime,'size'], loc=uprime)[0])


