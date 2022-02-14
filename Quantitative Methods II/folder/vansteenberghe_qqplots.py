#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 16:01:51 2022
QMF 2022

Quantile-Quantile plots

@author: Eric Vansteenberghe
"""

import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import statsmodels.api as sm # for Q-Q plots

ploton = False

#%% QQ plots

# number of generated points
Ni = 10
# generate points from a standard normal law
# use a Random Generator so we always have the same samples generated
y = np.random.default_rng(2022).normal(0, 1, Ni)

# plot a historgram
if ploton:
    plt.hist(y)

# Scipy function for Q-Q plot
# against the normal law
# normal law
if ploton:
    sm.qqplot(y, line='45')


# Manual Q-Q plot
# 1) sort values of y
y.sort()
# 2) we have Ni observations
# 2.1
print("for the first observations, the empirical value is", y[0])
print("below this value, we expect the have 10% of the population")
print("if the population follows a standard normal law, the threshold below which 10% of the population can be found is")
print(norm.ppf(.1))
#2.2
print("for the second observations, the empirical value is", y[1])
print("below this value, we expect the have 20% of the population")
print("if the population follows a standard normal law, the threshold below which 20% of the population can be found is")
print(norm.ppf(.2))
#2.3
print("for the third observations, the empirical value is", y[2])
print("below this value, we expect the have 20% of the population")
print("if the population follows a standard normal law, the threshold below which 30% of the population can be found is")
print(norm.ppf(.3))
#2.10
print("for the last and 10th observations, the empirical value is", y[9])
print("below this value, we expect the have 100% of the population")
print("if the population follows a standard normal law, the threshold below which 100% of the population can be found is")
print(norm.ppf(1))
# 3) generate the theoretical quantiles
x = []
for i in range(0,Ni):
    x.append(norm.ppf((i+1)/Ni))
    # to avoid loosing the last point, we can use Ni+1 at the denominator
    #x.append(norm.ppf((i+1)/(Ni+1)))
    
# 4) plot empirical against theoretical quantiles
if ploton:
    plt.plot(x, y, 'r.') # x vs y
    plt.plot(np.arange(-3,3,6/Ni),np.arange(-3,3,6/Ni),'k-') # identity line
    plt.xlabel('theoretical quantiles')
    plt.ylabel('empirical quantiles')
    plt.show()    

