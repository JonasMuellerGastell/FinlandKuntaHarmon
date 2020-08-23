#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 14:19:31 2020

@author: jonasmg
"""

import numpy as np
import pandas as pd
import pickle


path = '/home/jonasmg/Documents/FinlandKuntaHarmon/'

dfPop = pd.read_csv(path + 'Data/Demographics1880_1974.csv')
dfInfo =  pd.read_csv(path + 'Data/AllMoves.csv')


#%% Create the dictionary of all moves

yeardics = {k: dfPop.loc[dfPop['Year'] == k, 'code'].unique() for k in range(1880, 1975)}
for k in yeardics:
	yeardics[k].sort()
	
transitions = {}



for year in range(1880, 1975):
    yd = {}

    for c in yeardics[year]:
        ins = dfInfo.loc[(dfInfo['codeTarget'] == c) & (dfInfo['Year'] == year), ['codeSource', 'TotalDist', 'Total' ]]
        
        codesIns = ins.codeSource.tolist()
        numsIns = ins.TotalDist.tolist()
        maxIns = ins.Total.tolist()
        
        numsIns2 = [np.nanmin([numsIns[ind], maxIns[ind]]) for ind in range(len(numsIns))]
        
        numsOuts = dfInfo.loc[(dfInfo['codeSource'] == c) & (dfInfo['Year'] == year), ['TotalDist']]['TotalDist'].tolist()
        if len(numsOuts) == 0:
            numsOuts= [0]
            
        exists = dfPop.loc[(dfPop['code'] == c) & (dfPop['Year'] == year - 1), 'Total']    
        if len(exists) ==0:
            exists = 0
        else:
            exists = exists.iloc[0]
        print(c, year - 1)
        
        sendingPop = [dfPop.loc[(dfPop['code'] == codesInsK) & (dfPop['Year'] == year - 1), 'Total'].iloc[0] for codesInsK in codesIns]
        
        yd[c] = {'from':   codesIns , 
                 'howmanyIn' : numsIns,
                 'whatbase': sendingPop,
                 'howmanyOut': sum(numsOuts),
                 'howmanyEx': exists }
                   
    transitions[year] = yd

pickle.dump(transitions, open( path + "FromScratch/MuniTranslation18801974.p", "wb" ) )


#%% write the excel transition files

dfPop = dfPop[['kunta', 'code', 'year', 'PopulationEstimate']]
dfPop.columns = ['Name_Fi', 'id', 'Year', 'Total']

dfPop['Abs'] = dfPop['id'].apply(lambda x: str({x: 1}))
dfPop['Rel'] = dfPop['id'].apply(lambda x: str({x: 1}))



def Main(inyear, outyear, varsin):
	import numpy as np
	import pandas as pd

	global transitions

	transitionsUse = transitions
		
	inyear = int(inyear)
	outyear = int(outyear)

		
	currentyear = varsin	
	for year in range(inyear +1, outyear +1):
		print(year)
# 		print("%%%%%%%%%%%%%%%%%%% " + str(year)+ "  %%%%%%%%%%%%%")
		tdicY = transitionsUse[year]
		Ids = tdicY.keys()


		newyear = pd.DataFrame({k: [np.nan for m in range(len(Ids))] for k in varsin})
		newyear['id'] = Ids 
		
		for k in Ids:
			tdic = tdicY[k]
			 
			nextVar = {'id': k}
		
			if tdic['howmanyEx'] == 0:
				calc = {}
			else:
				try:
					currentAbs = eval(currentyear.loc[currentyear['id'] == k, 'Abs'].iloc[0])
				except:
					print(k)
					assert 1==2
				calc = {m:   ((tdic['howmanyEx'] - tdic['howmanyOut'])/tdic['howmanyEx']) * currentAbs[m] for m in currentAbs } 

			calc2 = []
			if len(tdic['from']) != 0:
				for indexer, inflow in enumerate(tdic['from']):
					try:
						c = eval(currentyear.loc[currentyear['id'] == inflow, 'Abs'].iloc[0])
					except:
						print(k)
						assert 1==2
					calc2.append({m: tdic['howmanyIn'][indexer]/tdic['whatbase'][indexer]*c[m] for m in c}) 
			
			for sub in calc2:
				for subkey in sub.keys():
					if subkey in calc.keys():
						calc[subkey] =  calc[subkey] + sub[subkey]
					else:
						calc[subkey] = sub[subkey]
			
			if calc == {}:
				calc = {k: 1}
				print(f"NO DATA FOR {k} ")
			nextVar['Abs'] = [str(calc)]
			
			


			calc2 = []
			baseline2  =[]
			if len(tdic['from']) != 0:
				for indexer, inflow in enumerate(tdic['from']):
					calc2.append(eval(currentyear.loc[currentyear['id'] == inflow, 'Rel'].iloc[0]))
					baseline2.append(tdic['howmanyIn'][indexer])

			if tdic['howmanyEx'] == 0:
				calc = {}
				baseline = 0
			else:
				c = eval(currentyear.loc[currentyear['id'] == k, 'Rel'].iloc[0])
				baseline = tdic['howmanyEx'] - tdic['howmanyOut']
				calc = {m: c[m]*baseline for m in c.keys()}

			total = baseline + sum(baseline2)

			calcFlat ={}  
			for indexer, sub in enumerate(calc2):
				for subkey in sub.keys():
					if subkey in calcFlat.keys():
						calcFlat[subkey] =  calcFlat[subkey] + baseline2[indexer] *sub[subkey]
					else:
						calcFlat[subkey] = baseline2[indexer] * sub[subkey]
			
			for subkey in calcFlat:
				if subkey in calc.keys():
					calc[subkey] = calc[subkey]  + calcFlat[subkey]
				else:
					calc[subkey] = calcFlat[subkey]
					
			for subkey in calc:
				calc[subkey] = calc[subkey]/total
			
			if calc == {}:
				calc = {k: 1}					
			nextVar['Rel'] = [str(calc)]			
				 
			newrow = pd.DataFrame.from_dict(nextVar, orient='columns')
			newrow['id'] = k
			newyear.loc[newyear['id'] == k, :] = [newrow.iloc[0]]
				
		currentyear = newyear.copy()

		currentyear.to_excel(path + f"Data/{inyear}{year}Translation.xlsx", index=False)

	return currentyear	




for k in range(94):
	print(f"%%%%%%%%%%%%%%%%% {1880 + k} %%%%%%%%%%%%%%%%%%%%%")
	start = dfPop.loc[dfPop['Year'] == 1880 + k, ['id', 'Abs', 'Rel']]
	end =Main(1880 + k, 1974, start, karel ='d')