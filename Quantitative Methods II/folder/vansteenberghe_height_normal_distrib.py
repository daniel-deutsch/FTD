#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QMF 2022
Heights looks normally distributed, but what about weights?

@author: Eric Vansteenberghe
"""

import matplotlib.pyplot as plt
import scipy.stats # for the t-test
from sklearn.ensemble import RandomForestRegressor
import statsmodels.formula.api as smf # for linear regressions
from statsmodels.stats.diagnostic import lilliefors
from scipy import stats
from scipy.stats import kurtosis
from scipy.stats import skew
import pandas as pd
import numpy as np
import os
from scipy.stats import pareto, lognorm, weibull_min, expon, logistic
import statsmodels.api as sm # for Q-Q plots


ploton = False

# We set the working directory
os.chdir('/Users/skimeur/Google Drive/empirical_finance')

df = pd.read_stata("data/replication_final.dta", convert_categoricals=False, columns= ["v002","v012","v024","v437","v438"])

# v002 household number
# v012 current age (respondent)
# v024 state
# v437 women's weight in kg
# v438 women's height in cm

statdesc = df.loc[:,["v012","v437","v438"]].describe().round(1)
statdesclatex = statdesc.to_latex()

ages = list(df.v012.unique())
ages.sort()


# keep only unique observations
df = df.drop_duplicates(subset=["v002","v012"])

if ploton:
    df.v437.hist(bins=50)
    df.v438.hist(bins=50)

# we seem to have unexpected outliers
# in this study, we are not focusing on the tail hence we drop outliers
df = df.loc[(df.v437<1600)&(df.v438<2000)&(df.v438>1200),:]

if ploton:
    df.v437.hist(bins=50)
    df.v438.hist(bins=50)

#%% Weight

if ploton:
    ax = df.v437.hist(bins=50, density=True)
    fig = ax.get_figure()
    fig.savefig('fig/Indian_weight.pdf')

# are the weights normally distributed?
# Kolmogorov-Smirnov two-sided test
stats.ks_2samp(df.v437, np.random.normal(df.v437.mean(), df.v437.std(), len(df)))
# we reject the null hypothesis
# Lilliefors test
lilliefors(df.v437, dist='norm') # we reject the null hypothesis, 
# our sample doesn't come from a normally distributed population

# take the log of weights
df['logv437'] = np.log(df.v437)

if ploton:
    ax = df.logv437.hist(bins=50, density=True)
    plt.close()


# T-test: is the mean return statistically different from mu?
# Two-sided test
# H0: the expected value of this sample made of (presumably) independent observations is equal to mu=df.logv437.mean()
scipy.stats.stats.ttest_1samp(df.logv437, df.logv437.mean())

#%% are the log weight normally distributed?

# visual inspection
# probability density function of a normal distribution
def pdfnormal(x, mui, sigmai):
    return (1 / np.sqrt((2*np.pi*sigmai**2))) * np.exp(-((x-mui)**2) / (2*sigmai**2))

xres = 0.0001  # resolution
# define the x-axis range based on CAC 40 data
x = np.arange(df.logv437.min(), df.logv437.max(), xres)
# normal distribution N(mui,sigmai)
pdf = pdfnormal(x, df.logv437.mean(), df.logv437.std())

# plot the probability density
if ploton:
    plt.plot(x, pdf, 'r', label="Normal PDF")
    plt.hist(df.logv437, bins=100, density=True)
    plt.plot(x, pdf, 'b', label="Normal PDF")
    plt.xlabel("log weight")
    plt.ylabel("Probability of occurence")
    plt.savefig('fig/Indian_logweight.pdf')
    plt.show()
    plt.close()


#%% Jarque-Bera test
JBstat = (len(df) / 6) * skew(df.logv437)**2 + (len(df) / 24 ) * (kurtosis(df.logv437) - 3)**2

# compare it to a chi 2 at 95% with two degrees of freedom
if JBstat > scipy.stats.chi2.ppf(q = 0.95, df = 2):
    print('we reject normality')
else:
    print('normaility of the distribution not rejected')

del JBstat

#%% chi-square goodness of fit
    
# first we need to put the data into histogramms, to have the frequency per bin
nb_bins = 50
obs_values, bin_edges = np.histogram(df.logv437, bins=nb_bins, density=True)

obs_values.sum()
expected_values = getattr(scipy.stats, 'norm').pdf(bin_edges[1:len(bin_edges)], loc=df.logv437.mean(), scale=df.logv437.std())

expected_values.sum()

#scipy.stats.chisquare(obs_values, expected_values, ddof=nb_bins-2)

dfchisq = pd.DataFrame([list(obs_values),list(expected_values)]).T
dfchisq.columns = ['observed values','expected values']

if ploton:
    ax = dfchisq.plot()
    fig = ax.get_figure()
    fig.savefig('fig/chisquaretest.pdf')

del nb_bins, obs_values, expected_values, dfchisq, bin_edges

#%% Kolmogorov - Smirnov test are the distribution the "same"?

# generate a random draw from a gaussian DGP
gaussianDGP = np.random.normal(df.logv437.mean(), df.logv437.std(), len(df))

# Kolmogorov-Smirnov two-sided test
stats.ks_2samp(df.logv437, gaussianDGP)
# we reject the null hypothesis
# Lilliefors test
lilliefors(df.logv437, dist='norm') # we reject the null hypothesis, 
# our sample doesn't come from a normally distributed population
# alternatively, Anderson-Darling test
stats.anderson(df.logv437, dist='norm')

# show the cumulative distribution function
if ploton:
    fig, ax = plt.subplots(ncols=1)
    ax1 = ax.twinx()
    ax.hist(df.logv437, 100, alpha=0.2, cumulative = True,color = 'blue')
    ax1.hist(df.logv437, 100, alpha=0.2, density=True, color = 'blue')
    ax.hist(gaussianDGP, 100, alpha=0.2, cumulative = True,color = 'red')
    ax1.hist(gaussianDGP, 100, alpha=0.2, density=True,color = 'red')
    plt.title('PDF and CDF, normal law in red')
    fig.savefig('fig/cdf_hist_cacnrom.pdf')

if ploton:
    fig, ax = plt.subplots(ncols=1)
    ax.hist(df.logv437, 100, alpha=0.2,cumulative = True,color = 'blue')
    ax.hist(gaussianDGP, 100, alpha=0.2,cumulative = True,color = 'red')
    plt.title('CDF, normal law in red')
    fig.savefig('fig/cdf_cacnrom.pdf')

#%% Q-Q plots

# normal law
if ploton:
    sm.qqplot(df.v437, line='r')
    
# logistic distribution on the log
if ploton:
    sm.qqplot(df.logv437, dist=logistic, line='r')

# exponential law
if ploton:
    sm.qqplot(df.loc[df.v437>df.v437.median(),'v437'], line='r', dist=expon)


# log-normal law
# you have to indicate the shape parameter in the distargs arguments
if ploton:
    shapelgn = lognorm.fit(df.v437)[0]
    sm.qqplot(df.v437, line='r', dist=lognorm, distargs=(shapelgn, ))

    
# Weibull law
# nota bene: in the sparams, you need to choose the shape parameter
if ploton:
    c = weibull_min.fit(df.v437)[0]
    sm.qqplot(np.log(df.v437), dist=weibull_min, distargs=(c, ), line='r')


# Pareto law
# nota bene: in the sparams, you need to define the scale parameter, here it is u=median
if ploton:
    sm.qqplot(np.log(df.v437), dist=pareto, distargs=(df.v437.median(), ), line='r')

    
#%% Exercise: try to find a better fit with another law
    
# work of João H. Dimas
# This code tests all probability distributions from scipy.stats and finds the best fit to rcac.
# It was ran the first time to automatically add the ones with errors to ignoreList. Then, I inserted them directly into the code to save processing time. 
# The ignored are the distributions that requires different parameters, so they can't be tested automatically.
# The list of distributions to ignore is larger than the ones that work. IOne could just iterate the working ones, but the code shows the original idea.
ignoreList = ['ksone','alpha','beta','betaprime','bradford','burr','burr12','fisk','chi','chi2','cosine','dgamma','dweibull','exponnorm','exponweib','exponpow','fatiguelife','foldcauchy','f','foldnorm','frechet_r','weibull_min','frechet_l','weibull_max','genlogistic','genpareto','genexpon','genextreme','gamma','erlang','gengamma','genhalflogistic','gompertz','gausshyper','invgamma','invgauss','invweibull','johnsonsb','johnsonsu','levy_stable','loggamma','loglaplace','lognorm','mielke','kappa4','kappa3','nakagami','ncx2','ncf','t','nct','pareto','lomax','pearson3','powerlaw','powerlognorm','powernorm','rdist','reciprocal','rice','recipinvgauss','semicircular','skewnorm','trapz','triang','truncexpon','truncnorm','tukeylambda','vonmises','vonmises_line','wrapcauchy','gennorm','halfgennorm','argus','kstwobign']

maxPValue = 0  
bestDist = None
bestSample = None  

for attr, value in scipy.stats.__dict__.items():
    try:
        if not attr in ignoreList and hasattr(value, "fit") and hasattr(value, "rvs") and hasattr(value, "name"):
            localMaxPValue = 0
            dist = getattr(scipy.stats, attr)
            print("Testing distribution: {}".format(dist.name))
            loc, scale = dist.fit(df.logv437)  
            
            # Since the sample is small, we run 100 times to find the highest p-value (ideally we would store the p-values, and analyse their distribution to choose the best fitting).
            for x in range(100):
                newseries = dist.rvs(loc=loc,scale=scale,size=len(df))
                statistic, pvalue = scipy.stats.ks_2samp(df.logv437,newseries)
                if pvalue > maxPValue:
                    maxPValue = pvalue
                    bestDist = dist
                    bestSample = newseries
                if pvalue > localMaxPValue:
                    localMaxPValue = pvalue
            print("Best p-value for {}: {:.4f}".format(dist.name, localMaxPValue))
    except Exception as ex:
        print("Error with distribution {}".format(attr))
        ignoreList.append(attr)
            
print("\nBest distribution: {}\nMax. p-value: {:.4f}".format(bestDist.name, maxPValue)) 
# Winner is Hyperbolic Secant, with second place going to Laplace distribution.
# Laplace was one first guess because of the tent shape.

# Get the "best" found sample and plot it
df['bestSample'] = bestSample

if ploton:
    plt.hist(df.logv437, 100, alpha=0.5, density=True, label='Weight distribution')
    plt.hist(df.bestSample, 100, alpha=0.5, density=True, label='Logistic distribution')
    plt.legend(loc='upper right')
    plt.title('Weight distribution versus {} PDF'.format(bestDist.name))
    plt.savefig('fig/distrib_fit_loop.pdf')
    plt.show()

# list the content of a library:
#scipy.stats.__dict__.items()

del ignoreList, maxPValue, bestDist, bestSample, loc, scale, newseries, statistic, pvalue, localMaxPValue, attr, x




#%% Height

if ploton:
    ax = df.v438.hist(bins=50, density=True)
    fig = ax.get_figure()
    fig.savefig('fig/Indian_height.pdf')

# are the weights normally distributed?
# Kolmogorov-Smirnov two-sided test
stats.ks_2samp(df.v438, np.random.normal(df.v438.mean(), df.v438.std(), len(df)))
# we do not always reject the null hypothesis at the 1 percent threshold
# Lilliefors test
lilliefors(df.v438, dist='norm') # we reject the null hypothesis, 
# our sample doesn't come from a normally distributed population

# CLT exercise

# now we consider that X is our population
# we will create nrs random samples from this population with nb individuals
nrs = 10**4
nb = 10**2
samples = []
for x in range(nrs):
    samples.append(np.random.choice(df.v438, size=nb))

samplesMeans = [np.mean(s) for s in samples]

# Lilliefors test for normality
lilliefors(samplesMeans, dist='norm')

if ploton:
    plt.hist(samplesMeans, bins=200, density=True, label="Samples means")
    plt.title("Central Limit Theorem")
    plt.legend(loc='upper right')
    plt.show()
    

barZ = [(s-np.mean(df.v438))/np.math.sqrt(np.std(df.v438, ddof=1)**2/nb) for s in samplesMeans]

# Lilliefors test for normality
lilliefors(barZ, dist='norm')

if ploton:
    plt.hist(barZ, bins=200, density=True, label="Samples means")
    plt.title("Central Limit Theorem")
    plt.legend(loc='upper right')
    plt.show()
    


#%% OLS

if ploton:
    ax = df.plot.scatter(x= "v438",y="v437")
    ax.set_xlabel("height")
    ax.set_ylabel("weight")
    fig = ax.get_figure()
    fig.savefig('fig/Indian_height_weight_scatter.pdf')

if ploton:
    ax = df.plot.scatter(x= "v438",y="logv437")
    ax.set_xlabel("height")
    ax.set_ylabel("weight")
    fig = ax.get_figure()
    fig.savefig('fig/Indian_height_logweight_scatter.pdf')

modelOLS = smf.ols('logv437 ~  v438',data = df).fit()
modelLaTeX = modelOLS.summary().as_latex()

#%% RANDOM FOREST REGRESSION

clf = RandomForestRegressor()
clfit = clf.fit(X=df.v438.values.reshape(-1, 1), y=df.logv437.values.ravel())

clfrestrict = RandomForestRegressor(n_estimators=10, max_depth=4, bootstrap=False)
clfitrestrict = clfrestrict.fit(X=df.v438.values.reshape(-1, 1), y=df.logv437.values.ravel())

#%% Predict
dfpred = pd.DataFrame(index=range(np.int(df.v438.min()),np.int(df.v438.max())),columns=['OLS','RF','RF restricted'])

dfpred.OLS = modelOLS.params[0] + modelOLS.params[1] * dfpred.index

dfpred.RF = clfit.predict(np.array(dfpred.index).reshape(-1, 1))

dfpred['RF restricted'] = clfitrestrict.predict(np.array(dfpred.index).reshape(-1, 1))

if ploton:
    ax = dfpred.plot()
    ax.set_xlabel("height")
    ax.set_ylabel("predicted log weight")
    fig = ax.get_figure()
    fig.savefig('fig/Indian_OLS_vs_RF.pdf')

