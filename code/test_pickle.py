#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Purpose: Example ingest and readout of the latest global and us JHU data
#
from datetime import datetime
from datetime import timedelta
from timeit import default_timer as timer
import os
from os import listdir, path
from os.path import isfile, join

import covid_structures as cs
import covid_tools as ct

if __name__ == '__main__':
	start = timer()
	now = datetime.now()
	dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
	print('Starting... (' + dt_string + ' Z)')
	
	world = ct.fetchWorld()
	
	print('\nDone.')
	duration = timer()-start
	print('Execution Time: {:0.2f}s'.format(duration))
