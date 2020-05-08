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
	
	props = ct.readConfig()
	world = ct.ingestData(props['COVID-19-DIR'])

	print('++++++++++++++++++++++++++++++++++++++++++++')
	world.exportStandard(path.abspath(path.join(path.dirname(__file__), '..', 'data', 'data_standard.txt')))
	world.exportTransposed(path.abspath(path.join(props['EXPORT-DIR'], 'data_transposed.txt')))
	world.exportShapefile(path.abspath(path.join(props['EXPORT-DIR'], 'data_covid.shp')))
	world.exportTransposedPGIS(path.abspath(path.join(props['EXPORT-DIR'], 'data_transposed.sql')))
	world.dump(path.abspath(path.join(path.dirname(__file__), '..', 'data', 'world.p')))
	
	print('\nReplicating...') # these could be copy commands
	world.exportStandard(path.abspath(path.join(props['EXPORT-DIR'], 'data_standard.txt')))
	world.dump(path.abspath(path.join(props['EXPORT-DIR'], 'world.p')))
	
	print('\nDone.')
	duration = timer()-start
	print('Execution Time: {:0.2f}s'.format(duration))
