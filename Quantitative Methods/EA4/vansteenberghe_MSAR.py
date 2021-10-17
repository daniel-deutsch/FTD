#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2021

@author: Eric Vansteenberghe
# Inspired by: https://www.statsmodels.org/stable/examples/notebooks/generated/markov_autoregression.html
"""

import statsmodels.api as sm
import pandas as pd
import os
import matplotlib.pyplot as plt


# to plot, set ploton to ploton to 1
ploton = False

# check if internet access
internetaccess = True

# change the working directory
os.chdir('//Users/skimeur/Google Drive/empirical_finance/')

#%% FRED GNP
if internetaccess:
    # r to disable escape
    base_url = r'https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}'
    
    # define the url for download, real US GNP
    #url = base_url.format(code='GDPC1')
    url = base_url.format(code='GNPC96')
    # import the data in a intermediary data frame
    df = pd.read_csv(url)
    df.index = pd.DatetimeIndex(df.DATE, freq='QS')
    df = pd.DataFrame(df.GNPC96)
    df.columns = ['GDP']
    df.to_csv('data/GDPC1.csv',index=True)
    # US RECESSIONS - NBER recessions
    base_url = r'https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}'
    url = base_url.format(code='USREC')
    # import the data in a intermediary data frame
    usrec = pd.read_csv(url)
    usrec.index = pd.to_datetime(usrec.DATE)
    usrec = pd.DataFrame(usrec.USREC)
    usrec.to_csv('data/usrec.csv', index=True)
else:
    df = pd.read_csv('data/GDPC1.csv', index_col=0)
    df.index = pd.DatetimeIndex(df.index, freq='QS')
    usrec = pd.read_csv('data/usrec.csv', index_col=0)

if ploton:
    df.plot()

#%% Quarterly US GDP growth rate

dx = 100 * (df - df.shift(1)) /  df.shift(1)
dx.dropna(inplace=True)

if ploton:
    dx.plot(title='US GDP growth rate')

#%% iid test on the US GNP quarterly growth rates
# $H_0$: independent and identical distribution of a random variable
sm.tsa.stattools.bds(dx)

#%% Hamilton 1989 data
if internetaccess:
    dta = pd.read_stata('https://www.stata-press.com/data/r14/rgnp.dta').iloc[1:]
    dta.index = pd.DatetimeIndex(dta.date, freq='QS')
    dta_hamilton = dta.rgnp
    dta_hamilton
    dta_hamilton.to_csv('data/dta_hamilton.csv', index=True)
else:
    dta_hamilton = pd.read_csv('data/dta_hamilton.csv', index_col=0)
    dta_hamilton.index = pd.DatetimeIndex(dta_hamilton.index, freq='QS')

#%% Both data sets
both = pd.concat([dx, dta_hamilton], axis=1)
both.dropna(inplace=True, how='any')

both.columns = ['Modern data', 'Original data']
if ploton:
    ax = both.plot()
    fig=ax.get_figure()
    fig.savefig('fig/Fed_versus_original_data.pdf')
    
both.columns = ['GDP','rgnp']

#%% AR order choice
# Fit an ARMA with the procedure and test with AIC or BIC
for coli in both.columns:
    ARMAfit = sm.tsa.arma_order_select_ic(both[coli], ic=['aic', 'bic'], trend='c', max_ma=0)
    print(coli)
    print('AIC',ARMAfit.aic_min_order)
    print('BIC',ARMAfit.bic_min_order)


# manual approach as in https://machinelearningmastery.com/grid-search-arima-hyperparameters-with-python/
import warnings
from math import sqrt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
 
# evaluate an ARIMA model for a given order (p,d,q)
def evaluate_arima_model(X, arima_order):
	# prepare training dataset
	train_size = int(len(X) * 0.66)
	train, test = X[0:train_size], X[train_size:]
	history = [x for x in train]
	# make predictions
	predictions = list()
	for t in range(len(test)):
		model = ARIMA(history, order=arima_order)
		model_fit = model.fit()
		yhat = model_fit.forecast()[0]
		predictions.append(yhat)
		history.append(test[t])
	# calculate out of sample error
	rmse = sqrt(mean_squared_error(test, predictions))
	return rmse
 
# evaluate combinations of p, d and q values for an ARIMA model
def evaluate_models(dataset, p_values, d_values, q_values):
	dataset = dataset.astype('float32')
	best_score, best_cfg = float("inf"), None
	for p in p_values:
		for d in d_values:
			for q in q_values:
				order = (p,d,q)
				try:
					rmse = evaluate_arima_model(dataset, order)
					if rmse < best_score:
						best_score, best_cfg = rmse, order
					print('ARIMA%s RMSE=%.3f' % (order,rmse))
				except:
					continue
	print('Best ARIMA%s RMSE=%.3f' % (best_cfg, best_score))
 
# evaluate parameters
p_values = range(0, 5)
d_values = [0]
q_values = [0]
warnings.filterwarnings("ignore")
evaluate_models(both['rgnp'].values, p_values, d_values, q_values)

#%%  Markov autoregression
mod_GDP = sm.tsa.MarkovAutoregression(both.GDP, k_regimes=2, order=4, switching_ar=False)
res_GDP = mod_GDP.fit()
res_GDP.summary()

if ploton:
    dta_hamilton.plot(title='Growth rate of Real GNP', figsize=(12,3))
    dx.plot(title='Growth rate of Real GNP', figsize=(12,3))

# Fit the model, in the paper they follow an AR(4)
mod_hamilton = sm.tsa.MarkovAutoregression(both.rgnp, k_regimes=2, order=4, switching_ar=False)
res_hamilton = mod_hamilton.fit()
res_hamilton.summary()

if ploton:
    fig, axes = plt.subplots(2, figsize=(7,7))
    ax = axes[0]
    ax.plot(res_hamilton.smoothed_marginal_probabilities[0])
    ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='k', alpha=0.1)
    ax.set_xlim(both.index[4], both.index[-1])
    ax.set(title='Smoothed probability of recession paper data')
    
    ax = axes[1]
    ax.plot(res_GDP.smoothed_marginal_probabilities[0])
    ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='k', alpha=0.1)
    ax.set_xlim(both.index[4], both.index[-1])
    ax.set(title='Smoothed probability of recession updated data')

    fig.tight_layout()
    fig.savefig('fig/inferred_probability_modern.pdf')


    
#%% Full time series, before 2020

ARMAfit = sm.tsa.arma_order_select_ic(dx.loc[dx.index.year<2020,:], ic=['aic', 'bic'], trend='c', max_ma=0)
print('AIC',ARMAfit.aic_min_order)
print('BIC',ARMAfit.bic_min_order)


# filter for years before 2020
mod_GDPfull = sm.tsa.MarkovAutoregression(dx.loc[dx.index.year<2020,:], k_regimes=2, order=3, switching_ar=False)
res_GDPfull = mod_GDPfull.fit()
res_GDPfull.summary()

    
#%% Full time series 2020 included

ARMAfit = sm.tsa.arma_order_select_ic(dx, ic=['aic', 'bic'], trend='c', max_ma=0)
print('AIC',ARMAfit.aic_min_order)
print('BIC',ARMAfit.bic_min_order)


# filter for years before 2020
mod_GDPfull2020 = sm.tsa.MarkovAutoregression(dx, k_regimes=2, order=3, switching_ar=False)
res_GDPfull2020 = mod_GDPfull2020.fit()
res_GDPfull2020.summary()

if ploton:
    fig, axes = plt.subplots(2, figsize=(7,7))
    ax = axes[0]
    ax.plot(res_GDPfull2020.smoothed_marginal_probabilities[0])
    ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='k', alpha=0.1)
    ax.set(title='Smoothed probability of recession')
    ax.set_xlim(dx.index[0], dx.index[-1])
    fig.tight_layout()
    
    ax = axes[1]
    ax.plot(res_GDPfull.smoothed_marginal_probabilities[0])
    ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='k', alpha=0.1)
    ax.set(title='Smoothed probability of recession, year 2020 excluded')
    ax.set_xlim(dx.index[0], dx.index[-1])
    fig.tight_layout()
    fig.savefig('fig/inferred_prob_2020_included.pdf')


