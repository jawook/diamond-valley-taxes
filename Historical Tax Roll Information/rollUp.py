# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 00:33:52 2023

@author: wilkijam
"""

import pandas as pd

fnList = ['DV2023.csv', 'TV2022.csv', 'TV2021.csv', 'TV2020.csv', 'TV2019.csv',
          'TV2018.csv', 'TV2017.csv', 'TV2016.csv', 'TV2014.csv']

consolList = pd.concat([pd.read_csv(f) for f in fnList])
consolList.to_csv('Consolidated.csv', index=False)