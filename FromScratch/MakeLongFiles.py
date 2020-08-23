#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 14:36:09 2020

@author: jonasmg
"""
f= '/home/jonasmg/Documents/FinlandKuntaHarmon/'
import pandas as pd

def read(year1, year2, f):
	crossf = f + 'Data/TransitionFiles/'
	xwalk = pd.read_excel(crossf + f'{year1}{year2}Translation.xlsx')
	xwalk['Abs'] = xwalk['Abs'].apply(eval)
	xwalk['Rel'] = xwalk['Rel'].apply(eval)
	return xwalk

def makeXWDF(year1, year2, f):
	xw = read(year1,year2, f)
	xw2 = pd.DataFrame( columns = ['idTarget', 'idSource', 'ValueAbs', 'ValueRel'])
	for index, row in xw.iterrows():
		i = row['id']
		absD = row['Abs']
		relD = row['Rel']
		dfAbs = pd.DataFrame.from_dict(absD, columns=['ValueAbs'], orient='index').reset_index()
		dfRel = pd.DataFrame.from_dict(relD, columns=['ValueRel'], orient='index').reset_index()
		dfT = dfAbs.merge(dfRel, on='index')
		dfT.columns =['idSource', 'ValueAbs', 'ValueRel']
		dfT['idTarget'] = i
		xw2 = xw2.append(dfT, sort=True)
	xw2 = xw2[['idTarget', 'idSource', 'ValueAbs', 'ValueRel']]
	xw2.to_csv(f'{f}Data/TransitionFiles/TransitionLong/LongVersion{year1}{year2}.csv', index=False, encoding='utf-8')
	
	
for year1 in range(1880, 1974):
	for year2 in range(1881, 1975):
		makeXWDF(year1, year2, f)