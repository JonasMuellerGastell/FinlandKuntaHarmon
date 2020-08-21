#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 10:21:38 2020

@author: jonasmg
"""

import pandas as pd
import numpy as np

import sys



def read(year1, year2, f):
	crossf = f + 'Data/TransitionFiles/'
	xwalk = pd.read_excel(crossf + f'{year1}{year2}Translation.xlsx')
	xwalk['Abs'] = xwalk['Abs'].apply(eval)
	xwalk['Rel'] = xwalk['Rel'].apply(eval)
	return xwalk

def makeXWDF(year1, year2, f):
	crossf = f + 'Data/TransitionFiles/'
	try:
		xw2 = pd.read_csv(crossf + f'TransitionLong/LongVersion{year1}{year2}.csv', encoding='utf-8')
	except:
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
		xw2.to_csv(crossf + f'TransitionLong/LongVersion{year1}{year2}.csv', index=False, encoding='utf-8')
	return xw2
		
		
def trans(df, absCols, relCols, year1, year2, f):
	xw2 = makeXWDF(year1, year2, f)
	dfTrans = xw2.merge(df, left_on = 'idSource', right_on='id', how= 'left')
	dfTrans.drop('id', axis=1, inplace=True)
	for x in absCols:
		dfTrans[x] = dfTrans.eval(x + '* ValueAbs') 
	for x in relCols:
		dfTrans[x] = dfTrans.eval(x + '* ValueRel') 
	dfTrans = dfTrans[['idTarget'] + absCols + relCols].groupby('idTarget').sum().reset_index()
	return dfTrans

#%%
def transCat(df, whichCols, year1, year2, f):
	df = df.join(pd.get_dummies(df[whichCols]))
	df.drop(whichCols, axis=1, inplace=True)
	dfTrans=  trans(df, [], df.columns.tolist()[1:], year1, year2, f)
	return dfTrans
# 	xw2 = makeXWDF(year1, year2)
# 	dfTrans = xw2.merge(df, left_on = 'idSource', right_on='id', how= 'left')
# 	dfTrans.drop('id', axis=1, inplace=True)



#%%
def sanity(df, year1, year2, absCols, relCols, idCol):
	if year2 <= year1:
		print('Cannot translate backwards in time, need year1 > year2')
		return None, None, None
	if idCol:
		code = idCol
	elif 'code' in df.columns:
		code = 'code'
	elif 'kunta' in df.columns and type(df['kunta'].iloc[0]) != str:
		code = 'kunta'
	elif 'id' in df.columns:
		code = 'id'
	elif 'grouper' in df.columns:
		code = 'grouper'
	else:
		print('Could not interpret id variable')
		return None, None, None
	df.rename({code: 'id'}, axis=1, inplace=True)
	
	if type(absCols) == str:
		absCols = [absCols]
	if type(relCols) == str:
		relCols = [relCols]
	if type(absCols) != list or type(relCols) != list or (absCols == [] and relCols == []):
		print('Did not understand column assignment')
		return None, None, None
	
	for x in absCols + relCols:
		if x not in df.columns:
			print('Typo in columns list')
			return None, None, None

	return df, absCols, relCols

def harmonize(df, year1, year2, absCols = [], relCols = [], idCol = False, f= '/home/jonasmg/Documents/FinlandKuntaHarmon/'):
	df, absCols, relCols = sanity(df, year1, year2, absCols, relCols, idCol)
	if df is None:
		return None
	dfNew = trans( df, absCols, relCols, year1, year2, f)			
	return dfNew


def categoricalHarmonize(df, year1, year2, whichCols,  idCol = False, f= '/home/jonasmg/Documents/FinlandKuntaHarmon/'):
	year1 = int(year1)
	year2 = int(year2)
	df, whichCols, _ = sanity(df, year1, year2, whichCols, [], idCol)
	if df is None:
		return None
	df = df[['id'] + whichCols]
	dfNew = transCat( df, whichCols, year1, year2, f)
	for col in whichCols:
		uniqs = df[col].unique()
		dfNew[col +'_catDict']  = '{'
		for x in uniqs:
			dfNew[col +'_catDict'] = dfNew[col +'_catDict'] + (dfNew[f'{col}_{x}'] > 0) * (f'"{x}" : ' + dfNew[f'{col}_{x}'].apply(str) + ', ') 
		dfNew[col +'_catDict']  = dfNew[col +'_catDict'].apply(lambda x: eval(x + '}'))
	return dfNew

	