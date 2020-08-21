#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 11:02:02 2020

@author: jonasmg
"""

import pandas as pd
import numpy as np
import pickle

def doImports(path):	
	dicIndex = pickle.load(open(path + 'Helper/YearCodeIndex.p', 'rb'))
	kuntas = pd.read_csv(path + 'kuntacodes_utf8.csv', encoding='utf-8')
	return dicIndex, kuntas

def extract(x, target):
	x = eval(x)
	if target in x.keys():
		return x[target]
	else:
		return 0


def asdict(df):
	a = df.iloc[:, 0].tolist()
	b = df.iloc[:, 1].tolist()
	return {a[k]: int(b[k]) for k in range(len(a))}
# def searchSuggestion(transition, code, ):
# 	transition['Contains'] = transition['Abs'].apply(lambda x: extract(x, code))
# 	d = transition.loc[transition.Contains != 0, ['id', 'Contains']]
# 	print(d.to_dict()	)
# 	maxVal = d['Contains'].max()
# 	print(code, maxVal)
# 	try:
# 		maxId = d.loc[d['Contains'] == maxVal, 'id'].iloc[0]
# 	except:
# 		print(code, "ERROR ERROR")
# 		maxId = None
# 	return maxId

def suggestion(code, year, yearIndex,  path, ):
	FIXLIST = pd.read_csv(path + 'Helper/NeverOccurrers.csv')
	FIXLIST = asdict(FIXLIST[['code',	'codeAgg']])
	minMax = yearIndex.get(int(code))
	if code in FIXLIST:
		return FIXLIST[int(code)] 
	elif minMax == None:
		print(f"%%%%% No code found for {code} %%%%%%")
		return np.nan

	elif year > minMax[1]:
		print(minMax)
		transition = pd.read_excel(path + f'TransitionFiles/{minMax[1]}{minMax[1]+1}Translation.xlsx')		
		transition['Contains'] = transition['Abs'].apply(lambda x: extract(x, code))
		d = transition.loc[transition.Contains != 0, ['id', 'Contains']]
		print(asdict(d)	)
		maxVal = d['Contains'].max()
		print(code, maxVal)
		try:
			maxId = d.loc[d['Contains'] == maxVal, 'id'].iloc[0]
			print(code, maxId)
		except:
			print(code, "ERROR ERROR")
			maxId = None
		return maxId
	elif year < minMax[0]:
		print(minMax)
		transition = pd.read_excel(path + f'TransitionFiles/{minMax[0]-1}{minMax[0]}Translation.xlsx')		
		d = eval(transition.loc[transition.id == code, ['Rel']].iloc[0, 0])
		print(d)
		a = list(d.values())
		b = list(d.keys())
		maxVal = max(a)
		maxId = b[a.index(maxVal)]
		print(code, maxId, maxVal)
		return maxId

def popChecker(df, yearvar, dicIndex, kuntas, suggestFixes, path):
	if suggestFixes:
		yearIndex = pickle.load(open(path + 'Helper/CodeMinMaxYearIndex.p', 'rb'))
		dic = {}
		
	if type(yearvar) == str: 
		for y in df[yearvar].tolist():
			for x in df[df[yearvar] == y].code.tolist():
				if x not in dicIndex[y]  and x == x and x != 'nan':
					a = kuntas.loc[kuntas.code == x, 'Name_Fi'].iloc[0]
					print(f"Kunta {a} is linked but does not exist in Population Census in  year {y}")
					if suggestFixes:
						dic[x] = suggestion(x, yearvar, yearIndex, path)
	elif type(yearvar) == int or type(yearvar) == float:
		for x in df.code.tolist():
			if x not in dicIndex[yearvar] and x == x and x != 'nan':
				a = kuntas.loc[kuntas.code == x, 'Name_Fi'].iloc[0]
				print(f"Kunta {a} is linked but does not exist in Population Census for given year {yearvar}")
				if suggestFixes:
						dic[x] = suggestion(x, yearvar, yearIndex, path)
	if suggestFixes:
		return dic
	else:
		return None
	
	
def provChecker(df):
	a = sum(df.code == 627)
	b = sum(df.code == 628)
	c = sum(df.code == 626)
	if a > 1 or b > 1 or c > 1:
		print(f"Pyhäjärvi:  U  appears {a} times, O appears {c} times, Viip occurs {b} times")
	a = sum(df.code == 284)
	b = sum(df.code == 283)
	if a > 1 or b > 1:
		print(f"Koski: Tl appears {a} times, Hl appears {b} times")
	a = sum(df.code == 294)
	b = sum(df.code == 35)
	if a > 1 or b > 1:
		print(f"Brändö: the huvilakaupunki appears {a} times, Brändö appears {b} times")


def urbanChecker(df, kuntas):
	urbanCheck = { 106: [106, 107],
		           220: [220, 221],
		           427: [427, 428],
		           612: [612, 613],
		           143: [143, 144],
		           430: [430, 431],
		           835: [835, 836],
		           529: [529, 530],
		           579: [579, 573],
		           609: [609, 610],
		           684: [684, 685],
		           895: [895, 896],
		           88:  [89, 88],
		           491: [492, 491],
		           593: [593, 594],
		           140: [141, 140],
		           297: [297, 298],
		           541: [541, 542],
		           179: [179, 180],
		           598: [598, 599],
		           743: [744, 743],
		           992: [992, 993],
		           205: [206, 205],
		           240: [240, 241],
		           698: [698, 699],
		           268: [268, 269],
		           313: [313, 314],
		           763: [763, 764],
		           929: [929, 930],
		           109: [109, 110],
		           893: [893, 894],}
	
	for k in urbanCheck:
		a = kuntas.loc[kuntas.code == urbanCheck[k][0], 'Name_Fi'].iloc[0]
		b = kuntas.loc[kuntas.code == urbanCheck[k][1], 'Name_Fi'].iloc[0]
		a2 = sum(df.code == urbanCheck[k][0])
		b2 = sum(df.code == urbanCheck[k][1])
		if a2 > 1 or b2  > 1:
			print(f"{k}: {a} occurs {a2} times, {b} occurs {b2} times")
	

def findCodes(df, names, province=False, urban=False,  yearvar = False, 
			   verbose=False, suggestFixes = False, 
			   path = '/home/jonasmg/Documents/FinlandKuntaHarmon/Data/'):
	assert type(names) in [str, list, dict]
	if type(names) == str:
		province=False
		urban=False
		nameVar = names
		print("No province or urban var declared")
	elif type(names) == list:
		print("assume ordering: name, province, urban")
		if province and urban:
			provinceVar = names[1]
			urbanVar = names[2]
		elif province:
			provinceVar = names[1]
		elif urban:
			urbanVar = names[1]
		nameVar = names[0]
	elif type(names) == dict:
		provinceVar = names.get('province')
		urbanVar = names.get('urban')
		nameVar = names['name']

	dicIndex, kuntas = doImports(path)

	if province and urban:
		k = 0
		for n in ['Name_Fi', 'Name_Sv', 'Name_AltGen', 'Name_Alt']:
			for p in ['province_Fi', 'province_Sv']:
				df = df.merge(kuntas[['code', n, p, 'Urban']], left_on=[nameVar, provinceVar, urbanVar], right_on=[n, p, 'Urban'], how='left', suffixes =['', f'_{k}'])
				df = df.drop([n,p, 'Urban'], axis=1)
				if k > 0:
					df.loc[df.code.isna(), 'code'] = df.loc[df.code.isna(), f'code_{k}']
					df = df.drop([f'code_{k}'], axis=1)
				k += 1
	elif province:
		k = 0
		for n in ['Name_Fi', 'Name_Sv', 'Name_AltGen', 'Name_Alt']:
			for p in ['province_Fi', 'province_Sv']:
				df = df.merge(kuntas[['code', n, p]], left_on=[nameVar, provinceVar], right_on=[n, p], how='left', suffixes =['', f'_{k}'])
				df = df.drop([n,p], axis=1)
				if k > 0:
					df.loc[df.code.isna(), 'code'] = df.loc[df.code.isna(), f'code_{k}']
					df = df.drop([f'code_{k}'], axis=1)
				k += 1
		urbanChecker(df, kuntas)
	elif urban:
		k = 0
		for n in ['Name_Fi', 'Name_Sv', 'Name_AltGen', 'Name_Alt']:
			df = df.merge(kuntas[['code', n, 'Urban']], left_on=[nameVar, urbanVar], right_on=[n, 'Urban'], how='left', suffixes =['', f'_{k}'])
			df = df.drop([n, 'Urban'], axis=1)
			if k > 0:
				df.loc[df.code.isna(), 'code'] = df.loc[df.code.isna(), f'code_{k}']
				df = df.drop([f'code_{k}'], axis=1)
			k += 1
		provChecker(df)
	else:
		k = 0
		for n in ['Name_Fi', 'Name_Sv', 'Name_AltGen', 'Name_Alt']:
			df = df.merge(kuntas[['code', n]], left_on=[nameVar], right_on=[n], how='left', suffixes =['', f'_{k}'])
			df = df.drop([n], axis=1)
			if k > 0:
				df.loc[df.code.isna(), 'code'] = df.loc[df.code.isna(), f'code_{k}']
				df = df.drop([f'code_{k}'], axis=1)
			k += 1
		provChecker(df)
		urbanChecker(df, kuntas)				
	print('How many unmatched?', sum(df.code.isna()))
	if verbose and len(df.loc[df.code.isna(), nameVar]) > 0:
		print(df.loc[df.code.isna(), nameVar].tolist())
	if verbose and yearvar:
		suggested = popChecker(df, yearvar, dicIndex, kuntas, suggestFixes, path)
		return df, suggested
	else:
		return df
