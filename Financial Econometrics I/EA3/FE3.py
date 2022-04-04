# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 21:04:40 2021

@author: Stéphane Roblet
"""

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from IPython.display import display
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.vector_ar.vecm import VECM, coint_johansen, select_order

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
df_aaa = pd.read_csv("aaa.csv", names=['date', 'valueaaa'], parse_dates=['date'], skiprows=[0], na_values='.')
df_govbonds = pd.read_csv("govbonds.csv", names=['date', 'valuegov'], parse_dates=['date'], skiprows=[0], na_values='.')
df_sp500 = pd.read_csv("SP.csv", names=['date', 'logS&P500'], parse_dates=['date'], skiprows=[0], na_values='.')

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
df_sp500["logS&P500"] = np.log(df_sp500['logS&P500'])



plt.show()

df = pd.merge(df_aaa[['date', 'valueaaa']], df_govbonds[['date', 'valuegov']], on='date', how='inner').rename(columns={ 'diff_x': 'diff_aaa', 'diff_y': 'diff_govbonds' })
df = df.merge(df_sp500[['date', 'logS&P500']], on='date', how='inner').rename(columns={ 'diff': 'diff_sp500' })
df.set_index('date', inplace=True)
df


#hypothesis =  linear trend
#we select a lag of 1 
jres = coint_johansen(df, det_order=1, k_ar_diff=1)

#the cointegration rank is equal to 0.
#The result is the same wether we are considering the eigenvalue statistic or the trace statistic.
#None of the series can help improving the prediction of one of the series.
#None of the series is causal (in a Granger sense)
#Therefore, we need to estimate a VAR in first differences. 

# Obtains the first difference
df_aaa['diff'] = df_aaa['valueaaa'].diff()
df_govbonds['diff'] = df_govbonds['valuegov'].diff()
df_sp500['diff'] = df_sp500['logS&P500'].diff()

# Remove not available data
df_aaa.dropna(inplace=True)
df_govbonds.dropna(inplace=True)
df_sp500.dropna(inplace=True)

# Plot the original series and it's first difference
fig, axs = plt.subplots(2, 3, figsize=(21, 8))
axs[0, 0].plot(df_aaa['date'], df_aaa['valueaaa'])
axs[0, 0].set_title("AAA Corporate Bonds Yields")
axs[1, 0].plot(df_aaa['date'], df_aaa['diff'])
axs[1, 0].set_title("First Diff AAA Corporate Bonds Yields")
axs[0, 1].plot(df_govbonds['date'], df_govbonds['valuegov'])
axs[0, 1].set_title("US Governament Bond Yields")
axs[1, 1].plot(df_govbonds['date'], df_govbonds['diff'])
axs[1, 1].set_title("First Diff US Governament Bond Yields")
axs[0, 2].plot(df_sp500['date'], df_sp500['logS&P500'])
axs[0, 2].set_title("S&P500")
axs[1, 2].plot(df_sp500['date'], df_sp500['diff'])
axs[1, 2].set_title("First Diff S&P500")
plt.show()

dfVAR = pd.merge(df_aaa[['date', 'diff']], df_govbonds[['date', 'diff']], on='date', how='inner').rename(columns={ 'diff_x': 'diff_aaa', 'diff_y': 'diff_govbonds' })
dfVAR = dfVAR.merge( df_sp500[['date', 'diff']], on='date', how='inner').rename(columns={ 'diff': 'diff_sp500' })
dfVAR.set_index('date', inplace=True)
dfVAR

df_scores = pd.DataFrame()
best_fit = None
for p in range(10):
    model = VAR(dfVAR)
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

best_fit.summary()
#significative short term impact of aaa and govbonds on aaa
#significative short term impact of govbonds on govbonds
#significative short term impact of govbonds and s&p500 on s&p500



