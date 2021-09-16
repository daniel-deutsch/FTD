#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2020

Playing Perudo: what are your odds?

@author: Eric Vansteenberghe
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# number of dices
ndices = 30

# how many random draw do you want
tirages = 10**6

# create the draws
experience = np.random.randint(1,7,size=(ndices,tirages))

extracttoshow = experience[:,:10]

# count how many aces and 2's you got per experiment
countnum = np.count_nonzero(experience == 1, axis=0) + np.count_nonzero(experience == 2, axis=0)

# what is the mean of count
countnum.mean()

# chance for a calza
plt.hist(countnum, bins=list(range(1,ndices-5)), density=True)

# chance for a dudo
dudo = []

for i in range(1,ndices+1):
    dudo.append((countnum < i).sum())

# convert it in odds
dudo = [x / tirages for x in dudo]

# convert it to a data frame
dudo = pd.DataFrame(dudo, index=range(1, ndices+1))
# change column name and plot
dudo.columns = ['dudo chance']
dudo.plot()