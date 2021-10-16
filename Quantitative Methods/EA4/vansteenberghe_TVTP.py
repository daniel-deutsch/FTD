#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2021

Filardo, 1994 replication: Business-Cyc e Phases and Their Transitions Dynamics
Based on: https://www.statsmodels.org/stable/examples/notebooks/generated/markov_autoregression.html

@author: Eric Vansteenberghe
"""

import numpy as np
import statsmodels.api as sm
import pandas as pd
import os
import matplotlib.pyplot as plt
import requests
from io import BytesIO


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


#%% Get the Filardo dataset
filardo = requests.get('http://econ.korea.ac.kr/~cjkim/MARKOV/data/filardo.prn').content
dta_filardo = pd.read_table(BytesIO(filardo), sep=' +', header=None, skipfooter=1, engine='python')
dta_filardo.columns = ['month', 'ip', 'leading']
dta_filardo.index = pd.date_range('1948-01-01', '1991-04-01', freq='MS')

dta_filardo['dlip'] = np.log(dta_filardo['ip']).diff()*100
# Deflated pre-1960 observations by ratio of std. devs.
# See hmt_tvp.opt or Filardo (1994) p. 302
std_ratio = dta_filardo['dlip']['1960-01-01':].std() / dta_filardo['dlip'][:'1959-12-01'].std()
dta_filardo['dlip'][:'1959-12-01'] = dta_filardo['dlip'][:'1959-12-01'] * std_ratio

dta_filardo['dlleading'] = np.log(dta_filardo['leading']).diff()*100
dta_filardo['dmdlleading'] = dta_filardo['dlleading'] - dta_filardo['dlleading'].mean()

if ploton:
    dta_filardo['dlip'].plot(title='Standardized growth rate of industrial production', figsize=(13,3))
    plt.figure()
    dta_filardo['dmdlleading'].plot(title='Leading indicator', figsize=(13,3))
    
    
mod_filardo = sm.tsa.MarkovAutoregression(
    dta_filardo.iloc[2:]['dlip'], k_regimes=2, order=4, switching_ar=False,
    exog_tvtp=sm.add_constant(dta_filardo.iloc[1:-1]['dmdlleading']))

np.random.seed(12345)
res_filardo = mod_filardo.fit(search_reps=20)
res_filardo.summary()

#%% compare with recessions



if ploton:
    fig, ax = plt.subplots(figsize=(12,3))

    ax.plot(res_filardo.smoothed_marginal_probabilities[0])
    ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='gray', alpha=0.2)
    ax.set_xlim(dta_filardo.index[6], dta_filardo.index[-1])
    ax.set(title='Smoothed probability of a low-production state')
    fig.savefig('fig/filardo_TVTP.pdf')
    
if ploton:
    res_filardo.expected_durations[0].plot(title='Expected duration of a low-production state', figsize=(12,3))


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
    df.to_csv('data/INDPRO.csv', index=True)
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
mod_INDPRO = sm.tsa.MarkovAutoregression(
    dx.iloc[2:]['INDPRO'], k_regimes=2, order=4, switching_ar=False,
    exog_tvtp=sm.add_constant(dx.iloc[1:-1]['SandP']))

np.random.seed(12345)
res_INDPRO = mod_INDPRO.fit(search_reps=100)
res_INDPRO.summary()

#%% compare with recessions


if ploton:
    plt.figure(3)
    fig, ax = plt.subplots(figsize=(12,3))
    ax.plot(res_INDPRO.smoothed_marginal_probabilities[0])
    ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='gray', alpha=0.2)
    ax.set_xlim(dx.index[6], dx.index[-1])
    ax.set(title='Smoothed probability of a low-production state')
    fig.savefig('fig/TVTP_INDPRO.pdf')
    plt.show()
    
if ploton:
    plt.figure(4)
    res_INDPRO.expected_durations[0].plot(title='Expected duration of a low-production state', figsize=(12,3))


#%% Year 2020 out
dx2020out = dx.loc[(dx.index.year<2020),:]

#%% calibrate the model
mod_INDPRO2020out = sm.tsa.MarkovAutoregression(
    dx2020out.iloc[2:]['INDPRO'], k_regimes=2, order=4, switching_ar=False,
    exog_tvtp=sm.add_constant(dx2020out.iloc[1:-1]['SandP']))

np.random.seed(12345)
res_INDPRO2020out = mod_INDPRO2020out.fit(search_reps=100)
res_INDPRO2020out.summary()

#%% compare with recessions


if ploton:
    plt.figure(3)
    fig, ax = plt.subplots(figsize=(12,3))
    ax.plot(res_INDPRO2020out.smoothed_marginal_probabilities[0])
    ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='gray', alpha=0.2)
    ax.set_xlim(dx2020out.index[6], dx2020out.index[-1])
    ax.set(title='Smoothed probability of a low-production state')
    fig.savefig('fig/TVTP_INDPRO_withou2020.pdf')
    plt.show()
    
if ploton:
    plt.figure(4)
    res_INDPRO2020out.expected_durations[0].plot(title='Expected duration of a low-production state', figsize=(12,3))

