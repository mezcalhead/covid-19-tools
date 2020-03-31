#!/usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
import sys
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import time
import cf_model

# data we have
# list of lines

size = 14
case_data = np.zeros(shape=(size,1), dtype = np.int8)
case_data[0] = 5
case_data[1] = -1
case_data[2] = 5
case_data[3] = -1
case_data[4] = -1
case_data[5] = -1
case_data[6] = 14
case_data[7] = 21
case_data[8] = 23
case_data[9] = 31
case_data[10] = 39
case_data[11] = 51
case_data[12] = 64
case_data[13] = 79

print(case_data)
print(case_data[6:])
print(case_data[6:] / case_data[6])
#if (True): sys.exit('')

# case_data[2] = 5
# case_data[6] = -1
# case_data[7] = -1
#case_data[8] = 3
#case_data[11] = 63
# case_data[10] = -1
# case_data[11] = -1
ndays = 3

base_date = datetime(2020, 3, 14)
date_data = np.array([base_date + timedelta(days=i) for i in range(size)])

#try:
plt, popt, rsqd, fig, ax, xm_data, ym_data = cf_model.calculate(date_data, case_data, \
	ndays, "Puerto Rico", 'Cases', 'EXP', plot_data = True, yavg_data = None)
plt.savefig('foo_exp.png')
plt.close(fig)
print('R-Squared: ' + '{0:.3f}'.format(rsqd) + ' POPT: ' + '{0:.3f}'.format(popt[0]) + ', ' + '{0:.3f}'.format(popt[1]))

# plt, popt, rsqd = cf_model.calculate(date_data, case_data, ndays, 'Puerto Rico', 'Cases', 'SIGMOID')
# plt.savefig('foo_sigmoid.png')
# print('R-Squared: ' + str(rsqd))

# plt = cf_model.calculate(date_data, case_data, ndays, 'Puerto Rico', 'Cases', 'POLY3')
# plt.savefig('foo_sigmoid.png')

#except Exception as e:
#	print(e)
