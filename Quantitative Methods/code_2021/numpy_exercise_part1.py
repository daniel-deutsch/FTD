"""
Eric Vansteenberghe
Quantitative Methods in Finance
Beginner exercise with numpy - part 1
2021
"""

import requests

# change to your directory if you want to be able to export figures in a precise folder
os.chdir('//Users/skimeur/Google Drive/empirical_finance/')

#%% first section, discover basic numpy functions
import numpy

#%% Exponential function

# return exponential of 1.5
numpy.exp(1.5)

# create to arrays, x1 and x2
x1 = numpy.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

x2 = numpy.arange(10)

# test that x1 = x2
x1 == x2

# check the sum, true = 1, false = 0
sum(x1 == x2)

# apply the exponential function to all elements of x1
y1 = numpy.exp(x1)

import matplotlib.pyplot as plt
import numpy

# plot y1 as a function of x1
plt.plot(x1,y1)

# if we want a more precise plot
x3 = numpy.arange(0,10,0.1)
y3 = numpy.exp(x3)
plt.plot(x3,y3)
#plt.savefig('fig/exponentialplot.pdf')

import matplotlib.pyplot as plt
#%% Define your own function
import numpy


# Define our own function y = x^2 + x -2
def my_f(x):
    return x**2 + x - 2

y_f = my_f(x1)

plt.plot(x1,y_f)

#%% Find roots

import matplotlib.pyplot as plt
import numpy

# Manual search for the root
my_f(0) == 0

my_f(1) == 0

my_f(2) == 0

# The for loop concept
for element in x1:
    print(element)

# Do a loop over all elements in x1 to search for the root(s)
for element in x1:
    if my_f(element) == 0:
        print('0=f(x) for x=',element)

# Actually there is a function that already exists to search for roots
from scipy.optimize import fsolve

# to get help on fsolve, type cmd + i in front of the line
fsolve(my_f,0)

# define a second function
def second_f(x):
    return numpy.cos(x**2)
    
# find the root of this function
sol = fsolve(second_f,10)

x3 = numpy.arange(-10,10,0.1)
y3 = second_f(x3)
plt.plot(x3,y3)
#plt.savefig('fig/cossquared.pdf')

#%% fixed-point iteration

import matplotlib.pyplot as plt
import numpy

# BABYLONIAN METHOD

def fpi(func, a, x0, nint):
    n = 0
    y = x0
    while n < nint:
        y = func(a, y)
        n += 1
    return y

def babylonian_m(a, x):
    return .5 * (a/x + x)
    
# apply the fixed-point iteration
a = 40 # the number we want the square root of
x0 = 6 # our starting guess
nint = 10 # the number of iteration
print("estimate of sqrt(",a,") with",x0,"as starting guess and", nint,"iterations: ", fpi(babylonian_m, a, x0, nint))
# check with the actual square root
print("the actual sqrt(",a,"):",numpy.sqrt(a))

# BANACH FIXED POINT THEOREM
x0 = 1
nint = 30
# fixed-point iteration
def fcos(x):
    return numpy.cos(x) - x
x_fcos = fsolve(fcos,1)
y = x0
n = 1
q = 0.85
while n < nint:
    y = numpy.cos(y)
    print("we verify the convergence",numpy.abs(y-x_fcos) < numpy.abs(x0 - numpy.cos(x0)) * (q**n) / (1-q))
    n += 1
    
# ANOTHER FUNCTION

#%% Gradient descent
    
import matplotlib.pyplot as plt
import numpy

next_x = 6  # We start the search at x=6
gamma = 0.01  # Step size multiplier
precision = 0.00001  # Desired precision of result
max_iters = 10000  # Maximum number of iterations

# Original function
def f_orig(x):
    return x**4 - 3*x**3 + 2

# Derivative function
def df(x):
    return 4 * x ** 3 - 9 * x ** 2


for _ in range(max_iters):
    current_x = next_x
    next_x = current_x - gamma * df(current_x)

    step = next_x - current_x
    if abs(step) <= precision:
        break

print("Minimum at ", next_x)
print("Minimum is", f_orig(next_x))

# The output for the above will be something like
# "Minimum at 2.2499646074278457"

x4= numpy.arange(-3, 4, 0.1)
y4 = f_orig(x4)
plt.plot(x4,y4)
#plt.savefig('fig/gradientdescent.pdf')

