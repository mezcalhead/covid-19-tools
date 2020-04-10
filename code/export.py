#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Purpose: Ingest JHU CSSE's Time Series Data Files, Merge, Normalize, and then Export
#
from datetime import datetime
from datetime import timedelta
from timeit import default_timer as timer
from os import listdir, path
from os.path import isfile, join

import covid_structures as cs
import covid_tools as ct

if __name__ == '__main__':
	start = timer()
	now = datetime.now()
	dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
	print('Starting... (' + dt_string + ' Z)')
	
	# export (assumes JHU's COVID-19 is installed under the root directory as COVID-19-TOOLS)
	basepath = path.abspath(path.join(path.dirname(__file__), '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'))
	world = ct.ingestData(basepath)
	world.exportStandard(path.abspath(path.join(path.dirname(__file__), '..', 'data', 'data_standard.txt')))
	world.exportTransposed(path.abspath(path.join(path.dirname(__file__), '..', 'data', 'data_transposed.txt')))
	world.exportShapefile(path.abspath(path.join(path.dirname(__file__), '..', 'data', 'data_covid.shp')))
	
	print('\nDone.')
	duration = timer()-start
	print('Execution Time: {:0.2f}s'.format(duration))
