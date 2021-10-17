# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 21:04:40 2021

@author: Stéphane Roblet
"""

import warnings

import numpy as np
import pandas as pd
from IPython.display import display
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import statsmodels.api as sm
from statsmodels.tsa.vector_ar.vecm import VECM,select_order


# Ignore warnings
warnings.filterwarnings('ignore')

# Matplotlib styles
plt.style.use('ggplot')
plt.rcParams.update({
    'figure.figsize': (15, 4),
    'axes.prop_cycle': plt.cycler(color=["#4C72B0", "#C44E52", "#55A868", "#8172B2", "#CCB974", "#64B5CD"]),
    'axes.facecolor': "#EAEAF2"
})

# Import data
df_aaa = pd.read_csv("aaa.csv", names=['date', 'value'], parse_dates=['date'], skiprows=[0], na_values='.')
df_govbonds = pd.read_csv("govbonds.csv", names=['date', 'value'], parse_dates=['date'], skiprows=[0], na_values='.')
df_sp500 = pd.read_csv("sp500.csv", names=['date', 'value'], parse_dates=['date'], skiprows=[0], na_values='.')

# Ignore day in datetime
df_aaa['date'] = df_aaa['date'].astype('datetime64[M]')
df_govbonds['date'] = df_govbonds['date'].astype('datetime64[M]')
df_sp500['date'] = df_sp500['date'].astype('datetime64[M]')

# Drop duplicates
df_aaa.drop_duplicates('date', inplace=True, ignore_index=True)
df_govbonds.drop_duplicates('date', inplace=True, ignore_index=True)
df_sp500.drop_duplicates('date', inplace=True, ignore_index=True)

# Remove not available data
df_aaa.dropna(inplace=True)
df_govbonds.dropna(inplace=True)
df_sp500.dropna(inplace=True)


# Remove not available data
df_aaa.dropna(inplace=True)
df_govbonds.dropna(inplace=True)
df_sp500.dropna(inplace=True)

# Plot the original series and it's first difference
fig, axs = plt.subplots(2, 3, figsize=(21, 8))
axs[0, 0].plot(df_aaa['date'], df_aaa['value'])
axs[0, 0].set_title("AAA Corporate Bonds Yields")
axs[1, 0].plot(df_aaa['date'], df_aaa['value'])
axs[1, 0].set_title("First Diff AAA Corporate Bonds Yields")
axs[0, 1].plot(df_govbonds['date'], df_govbonds['value'])
axs[0, 1].set_title("US Governament Bond Yields")
axs[1, 1].plot(df_govbonds['date'], df_govbonds['value'])
axs[1, 1].set_title("First Diff US Governament Bond Yields")
axs[0, 2].plot(df_sp500['date'], df_sp500['value'])
axs[0, 2].set_title("S&P500")
axs[1, 2].plot(df_sp500['date'], df_sp500['value'])
axs[1, 2].set_title("First Diff S&P500")
plt.show()

df = pd.merge(df_aaa[['date', 'value']], df_govbonds[['date', 'value']], on='date', how='inner').rename(columns={ 'diff_x': 'diff_aaa', 'diff_y': 'diff_govbonds' })
df = df.merge(df_sp500[['date', 'value']], on='date', how='inner').rename(columns={ 'diff': 'diff_sp500' })
df.set_index('date', inplace=True)
df

vec_rank1 = VECM.select_coint_rank(df, det_order = 1, k_ar_diff = 1, method = 'trace', signif=0.01)
print(vec_rank1.summary())

#hypothesis =  linear trend
#we select a lag of 1 
jres = coint_johansen(df, det_order=1, k_ar_diff=1)

#the cointegration rank is at most equal to 1 at a 1% risk level
#The result is the same wether we are considering the eigenvalue statistic or the trace statistic.
#From our previous result, we conclude that there exists one cointegrating equation at a 0.01 level.


X = df[['value_y','value_x']]
Y = df['value']
model = sm.OLS(Y, X).fit()

 
print_model = model.summary()
print(print_model)

#Interpretation ? Other tests to perform ?


#We select the order p for a VAR in levels
df_scores = pd.DataFrame()
best_fit = None
for p in range(10):
    model = VAR(df)
    model_fit = model.fit(p)
    df_scores = df_scores.append({
        'order': p,
        'AIC': model_fit.aic,
        'BIC': model_fit.bic, 
        'FPE': model_fit.fpe, 
        'HQIC': model_fit.hqic
    }, ignore_index=True)
    best_fit = model_fit if p == 0 else model_fit if model_fit.aic < best_fit.aic else best_fit
    
display(df_scores)
print(f"\nFrom the results shown above we can see that the model that uses {best_fit.k_ar} lags is the optimal one.\n")
#Therefore the order for the VECM will be p-1 = 1

#
VECM()
model = VECM(df, k_ar_diff=1, coint_rank=1)
vecm_res = model.fit()
vecm_res.summary()