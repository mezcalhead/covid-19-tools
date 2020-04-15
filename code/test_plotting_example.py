#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from os import path
from os.path import join

import covid_tools as ct

basepath = os.path.abspath(os.path.join(path.dirname(__file__), '..', 'tmp',))
if not os.path.exists(basepath): os.makedirs(basepath)

world = ct.fetchWorld()
ct.simplePlot(world, 'Global COVID-19', path.abspath(path.join(basepath, 'global1.png')), usedates = True)
ct.simplePlot(world, 'Global COVID-19', path.abspath(path.join(basepath, 'global2.png')), yscale = 'linear', xaxis='Day', usedates = False)
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

set = {}
area = world.getArea('China')
set[area.key()] = area
#set[world.key()] = world
area = world.getArea('US')
set[area.key()] = area
area = world.getArea('United Kingdom')
set[area.key()] = area
area = world.getArea('Italy')
set[area.key()] = area
area = world.getArea('Spain')
set[area.key()] = area
area = world.getArea('France')
set[area.key()] = area
area = world.getArea('Iran')
set[area.key()] = area
area = world.getArea('Austria')
set[area.key()] = area
#areas = ct.generateGuides(world, 'DEATHS', 10)
#for k, area in areas.items():
#	set[k] = area
ct.multiPlot(set, 'Plot', path.abspath(path.join(basepath, 'world_us.png')), 'DEATHS', 3, usedates = False)

