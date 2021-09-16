#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Eric Vansteenberghe
Quantitative Methods in Finance
Beginner exercise with pandas DataFrames - part 1
Select item by label or position
Matrix operations
Import csv data sets
Clean, rename columns, convert date information to python recognizable date format
Compute growth rates
Plot your data
Descriptive statistic of your data
2021
"""

import pandas as pd
import numpy as np


# to plot, set ploton to ploton to True
ploton = False

#%% Create a simple DataFrame
df = pd.DataFrame([[1,1,2],[3,4,5],[7,8,9]])

# rename the columns of the dataframe
df.columns = ['A','B','C']

# average of columns the dataframe
df.mean(axis = 0)
# sum of lines of the dataframe
df.sum(axis = 1)


#%% Finding location of an element in a DataFrame

slice1 = df.loc[ :,['A', 'C']]
slice2 = df.loc[1,['A', 'C']]
slice3 = df.loc[1:,:'B']

df.loc[1, 'A']

slice1i = df.iloc[ :,[0, 2]]
slice2i = df.iloc[1,[0, 2]]
slice3i = df.iloc[1:,:2]

#Row 2
df.iloc[2]
#Column C
df.T.iloc[2]

df.loc[1, 'A'] == df.iloc[1,0]

df_unstack = df.unstack()

df2 = df * 2

df.iloc[0] = 0

#%% Loop through a DataFrame

df3 = pd.DataFrame(index=[0,1,2], columns=[0,1,2])

for i in range(0,len(df)):
    for j in range(0,len(df.columns)):
        print("row",i,"col",j)
        df3.iloc[i,j] = df.iloc[i,j] * 2


df6 = pd.DataFrame(index=range(0,4),columns = range(0,4))

for i in range(0,len(df6)):
    for j in range(0,len(df6.columns)):
        df6.iloc[i,j] = i*j

del df, df2, df3, df6, df_unstack, slice1, slice1i, slice2, slice2i, slice3, slice3i, i, j,


#%% Matrix product 
# create a simple matrix
df = pd.DataFrame([[1,1,2],[3,4,5],[7,8,9]])

# rename the columns of the dataframe
df.columns = ['A','B','C']

# create a vector DataFrame, a columnc
colonne = pd.DataFrame([2,4,6])

# the index of colonne must be the df2 column name
colonne.index = df.columns

# perform a matrix times vector multiplication
out_mult = df.dot(colonne)

#%% Hadamard product

# we duplicate the colonne to form a square matrix
colonne = colonne.T.append([colonne.T]*2,ignore_index=True)

# multiply one df by the other, element by element
out_mult2 = df * colonne

#%% Inverse of the matrix
# we compute the inverse of the matrix
dfinv = np.linalg.inv(df)
# the product of a matrix (if non-singular) with its inverse is the identity matrix
print(df.dot(dfinv))

#%% Matrix product, eigenvalue, eigenvector and stability

# compute the eigenvalues and eigenvector of the DataFrame
eigen_df = np.linalg.eig(df)

# extract the eigenvectors
EVlist = pd.DataFrame(eigen_df[1])
# extract the first eigenvector
firstEV = pd.DataFrame(EVlist.iloc[:,0])
firstEV.index = df.columns

# Matrix * eigenvector == eigenvalue * eigenvector
df.dot(firstEV)
firstEV * eigen_df[0][0]

# eienvalues 
eigenvalues_df = eigen_df[0]
# are some eigenvalues greater than 1? How many?
sum(eigenvalues_df > 1)

del colonne, dfinv, out_mult, out_mult2

#%% Matrix product and stability

# Network of exposures:
dfa = pd.DataFrame([[0,0.4,0.3],[0.5,0,0.4],[0.6,0.1,0]])

# create the identity matrix
ident_mat = pd.DataFrame([[1,0,0],[0,1,0],[0,0,1]])
# or equivalent definition
ident_mat = pd.DataFrame(np.identity(3))

# NB: if you try with the following matrix, you find one eigenvalue greater than one and the convergence doesn't work
#dfa = pd.DataFrame([[0,0.9,0.7],[0.5,0,0.7],[0.6,0.7,0]])

eigen_dfa = np.linalg.eig(dfa)[0]
# how many eigenvalues are greater than one?
sum(eigen_dfa > 1)
# check that the matrix identity - dfa is non-singular (meaning that it can be inverted)
np.linalg.det((ident_mat-dfa)) != 0
# or checking that no eigenvalue is = 0
sum(np.linalg.eig((ident_mat-dfa))[0] == 0) == 0
# we take the inverse of identity - dfa
inv_dfa = pd.DataFrame(np.linalg.inv((ident_mat-dfa).values), dfa.columns, dfa.index)
# we create a shock vector, with shocks of 0.5%
chocs = pd.DataFrame([0.005,0.005,0.005])
# compute the shocks impact to infinity
out_loop = inv_dfa.dot(chocs)

# manual loop
# initial shocks values
out_loop_manual = chocs.copy(deep = True)
# initial exposure matrix
dfmult = dfa.copy(deep = True)
for i in range(0,1000):
    out_loop_manual = (dfmult).dot(chocs) + out_loop_manual
    dfmult = dfmult.dot(dfa)

# compare out_loop and out_loop_manual
out_loop - out_loop_manual
# try again with dfa = pd.DataFrame([[0,0.9,0.7],[0.5,0,0.7],[0.6,0.7,0]]), as there is an eigenvalue greater than one this should not work any more

del df, i, EVlist, chocs, out_loop, out_loop_manual, ident_mat, inv_dfa, firstEV, eigen_dfa, eigen_df, eigenvalues_df, dfa, dfmult

#%% Create manually a data frame

# we create a data frame with the evolution of the French population
pop = pd.DataFrame([66790,66763,66735,66710,66688,66672,66659,66644,66628])

# always useful to plot the data for visual inspection
#pop.plot()

# I don't think that the French population is declining:
# in fact we inversed the data, upside down
pop = pop.iloc[::-1]

#%% How to reverse a list (then an index) and how it works

# create a simple list
mylist = range(0,4)
# we wanted a list object
mylist = list(mylist)
# or more directly
mylist = list(range(0,4))
mylist[0:1:1]
mylist[0:2:1]
mylist[0:3:1]
mylist[0:4:1]
mylist[0:len(mylist):1]
# step of 2
mylist[0:len(mylist):2]
# omit the start and end, so use the default in python's
mylist[::]
# reverse the step (-1)
mylist[::-1]
# if we want to define start:end:step the stop is not obvious
mylist[3::-1]

#%% Plot our data set
# we can try to plot
#pop.plot()
# what you see is that now the index is incorrect
pop = pop.reset_index(drop = True)
if ploton == 1:
    pop.plot()

# now we want to use the calendar dates as index
dates = pd.date_range('2016-01', '2016-10', freq='M')

pop.index = dates

pop.columns = ['Population']

if ploton:
    pop.plot(title='French population in thousands')

# compute the monthly population change in France and plot it
change_pop = 100 * (pop/pop.shift(1)-1)
if ploton:
    change_pop.plot(title = 'Monthly French population change in percent')





