#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from os import path
from os.path import join

import covid_tools as ct

basepath = os.path.abspath(os.path.join(path.dirname(__file__), '..', 'tmp',))
if not os.path.exists(basepath): os.makedirs(basepath)

world = ct.fetchWorld()
area = world.getArea('US').getArea('Virginia') #.getArea('Chesapeake')
ct.simplePlot(area, area.a['name'] + ' COVID-19', path.abspath(path.join(basepath, 'test1.png')), 10, overlay=['avg','sum'], usedates = True)
ct.simplePlot(area, area.a['name'] + ' COVID-19', path.abspath(path.join(basepath, 'test2.png')), 1, overlay=['avg','sum'])
ct.simplePlot(area, area.a['name'] + ' COVID-19', path.abspath(path.join(basepath, 'test3.png')), 1, yscale = 'linear', usedates = True)

set = {}
for k in ['Virginia', 'Michigan', 'Louisiana']:
	area = world.getArea('US').getArea(k)
	set[area.key()] = area
ct.multiPlot(set, '3 States - Confirmed', path.abspath(path.join(basepath, 'test4.png')), 'CONFIRMED', 1)
ct.multiPlot(set, '3 States - Confirmed', path.abspath(path.join(basepath, 'test5.png')), 'CONFIRMED', 10)
ct.multiPlot(set, '3 States - Confirmed', path.abspath(path.join(basepath, 'test6.png')), 'CONFIRMED', 1, overlay=['avg','sum'], usedates = True)
ct.multiPlot(set, '3 States - Confirmed', path.abspath(path.join(basepath, 'test7.png')), 'CONFIRMED', 1, overlay=['avg','sum'], yscale='linear', usedates = True)