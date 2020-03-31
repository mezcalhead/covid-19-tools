#!/usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
# curve-fit() function imported from scipy 
from scipy.optimize import curve_fit 
import sys

from matplotlib import pyplot as plt

x_data = np.linspace(0.1, 1, num = 40) 
y_data = 3.45 * np.exp(1.334 * x_data) + np.random.normal(size = 40) 

# delete test
print(x_data)
x_data = np.delete(x_data, [4, 5, 6, 7, 14, 18, 20, 24, 29])
y_data = np.delete(y_data, [4, 5, 6, 7, 14, 18, 20, 24, 29])
print(x_data)

def test(x, a, b): 
	return a*np.exp(b*x) 

#lowerBounds = (0, 0)
#upperBounds = (1, 14) #np.Inf)
#parameterBounds = [lowerBounds, upperBounds]
parameterBounds = None

p0 = [1,1] # day 1, 1 case
param, param_cov = curve_fit(test, x_data, y_data, p0)
#print("Sine funcion coefficients:") 
#print(param) 
#print("Covariance of coefficients:") 
#print(param_cov) 
perr = np.sqrt(np.diag(param_cov))
print(perr)

#y_calc = (param[0]*(np.sin(param[1]*x_data)))
#y_calc = (param[0]*(np.exp(param[1]*x_data)))
#print(x_data)
x2_data = np.append(x_data, [1.25])
y_calc = (param[0]*(np.exp(param[1]*x2_data)))
print(x2_data)
#print(y_calc)

plt.plot(x_data, y_data, 'o', color ='red', label ="Reported Cummulative Cases") 
plt.plot(x2_data, y_calc, '--', color ='blue', label ="Projection") 
plt.legend()
plt.savefig('foo.png')
