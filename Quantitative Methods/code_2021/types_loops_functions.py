#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2021
Quantitative Methods in Finance

Types, loops, functions

@author: Eric Vansteenberghe
"""

# we create a variable that we name "growth"
growth = 1
# we want to know the type of the variable
print("the variable growth is of type:",type(growth))
# python considered it as an integer

# we now want to change the value
growth = 1.7
# we want to know the type of the variable
print("the variable growth is of type:",type(growth))
# python considered growth to be a floating number

# if we want to extract the integer part of growth:
int(growth)
# just for information, this is different as rounding!
round(growth)

print("the variable growth is of type:",type(growth))
# note that here we did not change growth type, if we wanted to
growth = int(growth)

# question: if you round growth into growth, was is now the type of growth?

# https://medium.com/@tyastropheus/tricky-python-i-memory-management-for-mutable-immutable-objects-21507d1e5b95
# some aspect of python memory management
x = 8
y = x
id(x)
id(y) # y has the same id as x (python manages memory, why create two id for the same info?)
x = 300 # we just changed x's id
y = 300
id(x)
id(y) # now y has a different id than x
y == x # same value, but different id (memory management)
del x, y

# we migth want to work with strings
country = 'France'
print("the type of the variable country is:", type(country))

# obviously, we cannot add a string with a float or integer:
try:
    test = growth + country
    print(test)
except TypeError:
    print('you cannot add a str with int')    

# question: create a variable growthTplus1 = 2.1 and try to add an integer with a float, what happens?

# we might want to define growth as a True or False dummy depending on other variables
# we take the data from the ECB statistical warehouse
# https://sdw.ecb.europa.eu/browseTable.do?org.apache.struts.taglib.html.TOKEN=bf39b6b002d0705df724dfda68f44fad&df=true&ec=&dc=&oc=&pb=&rc=&DATASET=0&removeItem=&removedItemList=&mergeFilter=&activeTab=MNA&showHide=&MAX_DOWNLOAD_SERIES=500&SERIES_MAX_NUM=50&node=9691186&legendRef=reference&legendPub=published&legendNor=&SERIES_KEY=320.MNA.Q.N.I8.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.V.N
# We do it manually as an introduction:

q2019Q1 = 2886662.47
q2018Q1	= 2812721.20
q2009Q1	= 2258741.06
q2008Q1	= 2354944.92

# is there a growth between 2018 Q1 and 2019 Q1?
growth = q2019Q1 > q2018Q1
print("the variable growth is of type:",type(growth))

# is there a growth between 2008 Q1 and 2009 Q1?
growth = q2009Q1	 > q2008Q1
print("In Europe, between the first quarter of 2008 and 2009, the GDP grew?",growth)

# As we deal with time series we might want to work with lists
quarters = ['q2008Q1','q2009Q1','q2018Q1','q2019Q1']
GDPs = [2354944.92,2258741.06,2812721.20,2886662.47]

# you can add an element to a list
GDPs.append(5)
# and remove an element
GDPs.remove(5)
# if the element is the last in the list, you can use .pop()

# if we are interested in the first observation, keep in mind that python index starting from 0
print(quarters[0])
# or equivalently
i = 0
print(quarters[i])
print(GDPs[i])
# we reproduce what we did above:
print("In Europe, between the first quarter of 2008 and 2009, the GDP grew?",GDPs[1] > GDPs[0])

# the concept of aliasing
# https://medium.com/@tyastropheus/tricky-python-i-memory-management-for-mutable-immutable-objects-21507d1e5b95
# we alias talias to GDPs list:
talias = GDPs
id(talias) == id(GDPs)
# or equivalently
talias is GDPs
# we make an operation on the mutable object GDPs
GDPs.append(5)
# this also impact talias
print(talias)
GDPs.pop()
# again
print(talias)
# now use .copy()
tnonalias = GDPs.copy()
tnonalias is GDPs
GDPs.append(5)
print(GDPs)
print(tnonalias)
GDPs.pop()

# as you noted, the list quarters is not "linked" to list GDPs
# we can define a dictionary
dictGDP = dict(zip(quarters, GDPs))
# you might wonder what zip() function does, then just goole it:
# https://docs.python.org/3.3/library/functions.html#zip
# which is equivalent to manually type:
dictGDPmanual = {'q2019Q1' : 2886662.47 ,'q2018Q1' :2812721.20,'q2009Q1' : 2258741.06,'q2008Q1' : 2354944.92}
# we reproduce what we did above:
print("In Europe, between the first quarter of 2008 and 2009, the GDP grew?", dictGDP['q2009Q1'] > dictGDP['q2008Q1'] )

# Condition
if dictGDP['q2009Q1'] > dictGDP['q2008Q1']:
    print("In Europe, between the first quarter of 2008 and 2009, the GDP grew")
elif dictGDP['q2009Q1'] == dictGDP['q2008Q1']:
    print("In Europe, between the first quarter of 2008 and 2009, the GDP stagnated")
else:
    print("In Europe, between the first quarter of 2008 and 2009, the GDP fell")

# for loop
# len() returns the lengths of a list
for i in range(0,len(GDPs)):
    print(i)
    
for i in range(0,len(GDPs)-1):
    print("Between",quarters[i],"and",quarters[i+1], "the GDP changed by ", GDPs[i+1]-GDPs[i])

# while loop, when did something happened?
# when did the GDP cross 2 400 000?
threshold = 2400000
i = 0  
while GDPs[i] < threshold:
    i += 1 # i = i + 1
print("GDP crossed 2 400 000 between", quarters[i-1], "and", quarters[i])
   
# function
# we define our first function
def growthGDP(GDPs, i, j):
    return (GDPs[j]-GDPs[i]) / GDPs[i]


for i in range(0,len(GDPs)-1):
    print((GDPs[i+1]-GDPs[i]) / GDPs[i])

for i in range(0,len(GDPs)-1):
    print(growthGDP(GDPs, i, i+1))

print("the GDP growth rate between 2008 and 2009 first quarters was", growthGDP(GDPs, 0, 1))

# nota bene: x/y - 1 should be == (x-y)/x, right?
(GDPs[1]-GDPs[0]) / GDPs[0] == GDPs[1]/ GDPs[0] - 1 # rounding aspects
(GDPs[1]-GDPs[0]) / GDPs[0]
GDPs[1]/ GDPs[0] - 1
import numpy as np
np.log(GDPs[1]) - np.log(GDPs[0]) # this is an expected approximation

# Which one should be use? x/y - 1 or(x-y)/x?

from decimal import *

getcontext().prec = 30
(Decimal(GDPs[1])- Decimal(GDPs[0])) / Decimal(GDPs[0])  
Decimal(GDPs[1])/ Decimal(GDPs[0]) - Decimal(1)

# we might want to return several results with one function
def growthGDP(GDPs, i, j):
    return (GDPs[j]-GDPs[i]) / GDPs[i], (GDPs[j]-GDPs[i]) 

ratioout, diffout = growthGDP(GDPs, 0, 1)
print("the GDP growth rate between 2008 and 2009 first quarters was", ratioout, 'the difference', diffout)


# work with numpy arrays
import numpy as np
GDPs = np.array([2886662.47,2812721.20,2258741.06,2354944.92])
# we reproduce what we did above:
print("In Europe, between the first quarter of 2008 and 2009, the GDP grew?",GDPs[2] > GDPs[3])

# work with pandas DataFrame
import pandas as pd
df = pd.DataFrame([2886662.47,2812721.20,2258741.06,2354944.92], index=['q2019Q1','q2018Q1','q2009Q1','q2008Q1'],columns = ['GDP'])
# we reproduce what we did above:
print("In Europe, between the first quarter of 2008 and 2009, the GDP grew?",df.loc['q2009Q1',:] > df.loc['q2008Q1',:])

df.loc['q2009Q1',:]

# we can now ennumerate:
for GDPi in df.GDP: # df.GDP is equivalent to df['GDP']
    if GDPi > threshold:
        print("GDP was above 2 400 000 at date", df.loc[df.GDP==GDPi,:].index)

# or nicer to read:
for GDPi in df.GDP:
    if GDPi > threshold:
        print("GDP was above 2 400 000 at date", df.loc[df.GDP==GDPi,:].index[0])
       
# some subtelties
# if we defined df pointing toward the list GDPs:
GDPlist = [2354944.92,2258741.06,2812721.20,2886662.47]
df2 = pd.DataFrame([[GDPlist]])
df2copy = df2.copy(deep=True)
# are both dataframes with the same id?
df2copy is df2
# are both dataframes with the same values?
df2copy == df2
# so we store a list in a "cell" of a DataFrame
df2.loc[0,0].append(4)
# then in this case, you modified the original GDPlist
# and this becomes confusing, because df2copy also got modified
df2copy == df2

        
# a speed test between numpy and pandas for matrix multiplications
import random
import scipy.sparse

# create numpy arrays
a = np.arange(100)
aa = np.arange(100, 200)

# create pandas Series
s = pd.Series(a)
ss = pd.Series(aa)

# create random index to chose from
i = np.random.choice(a, size=10)

# time speed of python to select array or Series indexes
%timeit a[i]
%timeit s[i]

# time speed of python for simple multiplication between numpy and pandas
%timeit a * aa
%timeit s * ss

# now we create a matrix and a vector and we compare a multiplication between numpy and pandas
densitymin = 0.1
densitymax = 0.2
#
densitymat = random.uniform(densitymin,densitymax)
M = scipy.sparse.rand(10,10,density= densitymat).A
V = scipy.sparse.rand(10,1,density= densitymat).A
Mnp = np.matrix(M)
Vnp = np.matrix(V)
Mpd = pd.DataFrame(M)
Vpd = pd.DataFrame(V)

%timeit Mnp @ Vnp
%timeit Mpd.dot(Vpd)

# numpy matrix multiplication close to 200 times faster!
def f(x):
    return x**2-1
list(map(f, [0,1,2,3,4,5]))

def f2(*x):
    return [x[i]**2-1 for i in range(len(x))]
f2([0,1,2,3,4,5])
