#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2021

McConnell 2000
Based on: https://www.statsmodels.org/stable/examples/notebooks/generated/markov_autoregression.html

@author: Eric Vansteenberghe
"""

import numpy as np
import statsmodels.api as sm
import pandas as pd
import os
import matplotlib.pyplot as plt



# to plot, set ploton to ploton to 1
ploton = True

# check if internet access
internetaccess = True

# change the working directory
os.chdir('//Users/skimeur/Google Drive/empirical_finance/')

#%% US recessions data
if internetaccess:
    # US RECESSIONS - NBER recessions
    base_url = r'https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}'
    url = base_url.format(code='USREC')
    # import the data in a intermediary data frame
    usrec = pd.read_csv(url)
    usrec.index = pd.to_datetime(usrec.DATE)
    usrec = pd.DataFrame(usrec.USREC)
    usrec.to_csv('data/usrec.csv', index=True)
else:
    usrec = pd.read_csv('data/usrec.csv', index_col=0)


#%% US industrial production and S&P 500 data

if internetaccess:
    # r to disable escape
    base_url = r'https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}'
    # define the url for download monthly US industrial production
    url = base_url.format(code='INDPRO')
    # import the data in a intermediary data frame
    df = pd.read_csv(url)
    df.index = pd.DatetimeIndex(df.DATE, freq='MS')
    df = pd.DataFrame(df.INDPRO)
    df.columns = ['INDPRO']
    df.to_csv('data/INDPRO.csv',index=True)
else:
    df = pd.read_csv('data/GINDPRO.csv', index_col=0)
    df.index = pd.DatetimeIndex(df.index, freq='QS')



sp500 = pd.read_csv('data/SandP_WSJ.csv')
sp500.index = pd.to_datetime(sp500.Date, format='%m/%d/%y')
sp500 = pd.DataFrame(sp500[' Close'])
sp500.columns = ['SandP']
sp500 = sp500.iloc[::-1]
sp500 = sp500.resample('MS').mean()

df = pd.concat([df, sp500], axis=1)
df.dropna(how='any', inplace=True)
colsdf = df.columns
df.columns = ['US industrial production','S&P 500']

if ploton:
    plt.figure(0)
    ax = df.plot(secondary_y=list(df.columns)[0])
    fig = ax.get_figure()
    fig.savefig('fig/USindprod_SandP500.pdf')
    
df.columns = colsdf
    
#%% Monthly returns
dx = (df/df.shift(1)) - 1
dx.dropna(inplace=True)

if ploton:
    plt.figure(1)
    dx.plot(secondary_y='INDPRO')


#%% calibrate the model
kregimes_Hamilton = 2
mod_INDPRO_Hamilton = sm.tsa.MarkovAutoregression(
    dx.iloc[2:]['INDPRO'], k_regimes=kregimes_Hamilton, order=1, switching_ar=False, switching_variance=False,
    exog_tvtp=sm.add_constant(dx.iloc[1:-1]['SandP']))

np.random.seed(12345)
res_INDPRO_Hamilton = mod_INDPRO_Hamilton.fit(search_reps=100)
res_INDPRO_Hamilton.summary()

#%% compare with recessions

constants_Hamilton = []
for i in range(kregimes_Hamilton):
    constants_Hamilton.append(res_INDPRO_Hamilton.params['const['+str(i)+']'])

if ploton:
    plt.figure(3)
    fig, ax = plt.subplots(figsize=(12,3))
    ax.plot(res_INDPRO_Hamilton.smoothed_marginal_probabilities[np.argmin(constants_Hamilton)])
    ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='gray', alpha=0.2)
    ax.set_xlim(dx.index[6], dx.index[-1])
    ax.set(title='Smoothed probability of a low-production state')
    #fig.savefig('fig/MCConnell_INDPRO_Hamilton.pdf')
    plt.show()
    


#%% calibrate the model
kregimes = 2
mod_INDPRO = sm.tsa.MarkovAutoregression(
    dx.iloc[2:]['INDPRO'], k_regimes=kregimes, order=1, switching_ar=False, switching_variance=True,
    exog_tvtp=sm.add_constant(dx.iloc[1:-1]['SandP']))

np.random.seed(12345)
res_INDPRO = mod_INDPRO.fit(search_reps=100)
res_INDPRO.summary()

#%% compare with recessions

constants = []
for i in range(kregimes):
    constants.append(res_INDPRO.params['const['+str(i)+']'])

if ploton:
    plt.figure(3)
    fig, ax = plt.subplots(figsize=(12,3))
    ax.plot(res_INDPRO.smoothed_marginal_probabilities[np.argmin(constants)])
    ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='gray', alpha=0.2)
    ax.set_xlim(dx.index[6], dx.index[-1])
    ax.set(title='Smoothed probability of a low-production state')
    fig.savefig('fig/MCConnell_INDPRO.pdf')
    plt.show()
    
if ploton:
    plt.figure(4)
    res_INDPRO.expected_durations[0].plot(title='Expected duration of a low-production state', figsize=(12,3))


#%% Using NFCI

if internetaccess:
    # r to disable escape
    base_url = r'https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}'
    # define the url for download monthly US industrial production
    url = base_url.format(code='INDPRO')
    # import the data in a intermediary data frame
    df = pd.read_csv(url)
    df.index = pd.DatetimeIndex(df.DATE, freq='MS')
    df = pd.DataFrame(df.INDPRO)
    df.columns = ['INDPRO']
    df.to_csv('data/INDPRO.csv',index=True)
else:
    df = pd.read_csv('data/GINDPRO.csv', index_col=0)
    df.index = pd.DatetimeIndex(df.index, freq='QS')

dfindprod = df.copy(deep=True)

if internetaccess:
    # r to disable escape
    base_url = r'https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}'
    # define the url for download monthly US industrial production
    url = base_url.format(code='NFCI')
    # import the data in a intermediary data frame
    df = pd.read_csv(url)
    df.index = pd.DatetimeIndex(df.DATE, freq='W-FRI')
    df = pd.DataFrame(df.NFCI)
    df.columns = ['NFCI']
    df.to_csv('data/NFCI.csv',index=True)
else:
    df = pd.read_csv('data/NFCI.csv', index_col=0)
    df.index = pd.DatetimeIndex(df.index, freq='WS')
    
df = df.resample('MS').mean()
df = pd.concat([dfindprod, df], axis=1)
df.dropna(how='any', inplace=True)
colsdf = df.columns
df.columns = ['US industrial production','NFCI']

if ploton:
    plt.figure(0)
    ax = df.plot(secondary_y=list(df.columns)[0])
    fig = ax.get_figure()
    fig.savefig('fig/USindprod_NFCI.pdf')
    
df.columns = colsdf
    
#%% Monthly returns
dx = df.copy(deep=True)
dx['INDPRO'] = (df['INDPRO']/df['INDPRO'].shift(1)) - 1
dx.dropna(inplace=True)

if ploton:
    plt.figure(1)
    dx.plot(secondary_y='INDPRO')


#%% calibrate the model
kregimes = 2
mod_INDPRO = sm.tsa.MarkovAutoregression(
    dx.iloc[2:]['INDPRO'], k_regimes=kregimes, order=1, switching_ar=False, switching_variance=True,
    exog_tvtp=sm.add_constant(dx.iloc[1:-1]['NFCI']))

np.random.seed(12345)
res_INDPRO = mod_INDPRO.fit(search_reps=100)
res_INDPRO.summary()

#%% compare with recessions

constants = []
for i in range(kregimes):
    constants.append(res_INDPRO.params['const['+str(i)+']'])

if ploton:
    plt.figure(3)
    fig, ax = plt.subplots(figsize=(12,3))
    ax.plot(res_INDPRO.smoothed_marginal_probabilities[np.argmin(constants)])
    ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='gray', alpha=0.2)
    ax.set_xlim(dx.index[6], dx.index[-1])
    ax.set(title='Smoothed probability of a low-production state')
    fig.savefig('fig/MCConnell_INDPRO_NFCI.pdf')
    plt.show()
