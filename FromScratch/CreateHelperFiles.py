#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 13:57:28 2020

@author: jonasmg
"""

import pandas as pd
import pickle as p

path = '/home/jonasmg/Documents/FinlandKuntaHarmon/'

df = pd.read_csv(path + 'Data/Demographics1880_1974.csv')

p1 = p.load(open(path + "Data/Helper/CodeMinMaxYearIndex.p", 'rb'))
p2 = p.load(open(path + "Data/Helper/YearCodeIndex.p", 'rb'))

a = df.groupby(['code'])['year'].min().reset_index()
a.columns = ['code', 'minY']
a['maxY'] =  df.groupby(['code'])['year'].max().reset_index()['year']
aD = {a.iloc[i, 0]: [int(a.iloc[i, 1]), int(a.iloc[i, 2])] for i in range(len(a))}

b = df.groupby('year')['code'].unique().reset_index()
bD = {b.iloc[i, 0]: list(b.iloc[i, 1]) for i in range(len(b))}

p.dump(aD, open(path + "Data/Helper/CodeMinMaxYearIndex.p", 'wb')) 
p.dump(bD, open(path + "Data/Helper/YearCodeIndex.p", 'wb')) 

