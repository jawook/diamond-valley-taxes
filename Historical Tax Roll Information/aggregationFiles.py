# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 17:50:15 2023

@author: wilkijam
"""

import camelot
import pandas as pd
import numpy as np

def newAssess(load):
    if load['Age'] == 'New':
        cNames = {0: 'Roll Number', 1: 'Legal Address', 2: 'Tax/Exempt', 
                  3: 'Prop Type Code', 4: 'Prop Type', 5:'Payer Type',
                  6: 'Land Value', 7: 'Impr. Value', 8: 'Other Value', 
                  9: 'Total Value'}
        delCols = ['PrevRN', 'PrevLA', 'PrevSA']
    elif load['Age'] == 'Old':
        cNames = {0: 'Roll Number', 1: 'Legal Address', 2: 'Tax/Exempt', 
                  3: 'Prop Type Code', 4: 'Prop Type', 5:'Payer Type',
                  6: 'Extra', 7: 'Land Value', 8: 'Impr. Value', 
                  9: 'Other Value', 10: 'Total Value'}
        delCols = ['PrevRN', 'PrevLA', 'PrevSA', 'Extra']
    tables = camelot.read_pdf(load['Town'] + str(load['Year']) + '.pdf', 
                              flavor='stream', pages='1-end', 
                              table_areas=load['Coords'], 
                              columns=load['Cols'])
    bigTab = tables[0].df.copy()
    bigTab.drop(0, inplace=True)
    for j in range(1, len(tables)):
        if tables[j].df.loc[0, 0][:4] == 'Code':
            continue
        bigTab = pd.concat([bigTab, tables[j].df.drop(0)], ignore_index=True)    
    bigTab.rename(columns=cNames, inplace=True)
    bigTab[['Street Address', 'Prop Subtype', 'Description']] = np.nan
    bigTab.replace('', np.nan, inplace=True)
    bigTab.loc[(bigTab['Legal Address'].isna()) & (~bigTab['Roll Number'].isna()),
                'Legal Address'] = bigTab['Tax/Exempt']
    bigTab.loc[~bigTab['Roll Number'].isna(), 'Tax/Exempt'] = np.nan
    bigTab['Street Address'] = bigTab['Legal Address'].shift(periods=-1)
    bigTab['Payer Type'] = bigTab['Payer Type'].shift(periods=-1)
    allowedPT = ['I  Individual', 'M  Municipal', 'C  Corporation', 'F  Federal',
                  'P  Provincial']
    bigTab.loc[~bigTab['Payer Type'].isin(allowedPT), 'Payer Type'] = np.nan
    bigTab.loc[~bigTab['Roll Number'].isna(), 'Description'] = bigTab['Land Value']
    bigTab['Land Value'] = bigTab['Land Value'].shift(periods=-2)
    bigTab['Impr. Value'] = bigTab['Impr. Value'].shift(periods=-2)
    bigTab['Other Value'] = bigTab['Other Value'].shift(periods=-2)
    bigTab['Total Value'] = bigTab['Total Value'].shift(periods=-2)
    bigTab['Tax/Exempt'] = bigTab['Tax/Exempt'].shift(periods=-2)
    bigTab['Prop Type Code'] = bigTab['Prop Type Code'].shift(periods=-2)
    bigTab['Prop Type'] = bigTab['Prop Type'].shift(periods=-2)
    bigTab['Prop Subtype'] = bigTab['Legal Address'].shift(periods=-2)
    bigTab.dropna(subset=['Land Value'], inplace=True)
    bigTab['Roll Number'].ffill(inplace=True)
    bigTab['Payer Type'].replace(['Taxable Total:', 'Exempt Total:'], np.nan, 
                                  inplace=True)
    bigTab['Payer Type'].ffill(inplace=True)
    bigTab['PrevRN'] = bigTab['Roll Number'].shift(periods=1)
    bigTab['PrevLA'] = bigTab['Legal Address'].shift(periods=1)
    bigTab['PrevSA'] = bigTab['Street Address'].shift(periods=1)
    bigTab.loc[bigTab['PrevRN'] == bigTab['Roll Number'], 
                'Legal Address'] = bigTab['PrevLA']
    bigTab.loc[bigTab['PrevRN'] == bigTab['Roll Number'], 
                'Street Address'] = bigTab['PrevSA']
    bigTab.dropna(subset=['Total Value'], inplace=True)
    bigTab.loc[bigTab['Roll Number'].isna(), 'Legal Address'] = np.nan
    bigTab['Legal Address'].ffill(inplace=True)
    bigTab['Payer Type'].ffill(inplace=True)
    bigTab['Land Value'] = bigTab['Land Value'].str.replace(',','').astype(int, errors='ignore')
    bigTab['Impr. Value'] = bigTab['Impr. Value'].str.replace(',','').astype(int, errors='ignore')
    bigTab['Other Value'] = bigTab['Other Value'].str.replace(',','').astype(int, errors='ignore')
    bigTab['Total Value'] = bigTab['Total Value'].str.replace(',','').astype(int, errors='ignore')
    bigTab['Roll Number'] = bigTab['Roll Number'].astype(int, errors='ignore')
    bigTab.dropna(subset=['Legal Address'], inplace=True)
    bigTab.drop(columns=delCols, inplace=True)
    bigTab.reset_index(inplace=True, drop=True)
    bigTab['Tax Year'] = load['Year']
    bigTab.to_csv(load['Town'] + str(load['Year']) + '.csv', sep=',', index=False)
    return bigTab

loads = {'DV2023': {'Town': 'DV', 'Year': 2023, 
                    'Coords': ['39, 540, 775, 40'], 
                    'Cols': ['100, 290, 315, 330, 465, 570, 620, 680, 725'],
                    'Age': 'New'},
         'TV2022': {'Town': 'TV', 'Year': 2022, 
                    'Coords': ['39, 540, 775, 40'], 
                    'Cols': ['100, 290, 315, 330, 465, 570, 620, 680, 725'],
                    'Age': 'New'},
         'TV2021': {'Town': 'TV', 'Year': 2021, 
                    'Coords': ['39, 540, 775, 40'], 
                    'Cols': ['100, 290, 315, 330, 465, 570, 620, 680, 725'],
                    'Age': 'New'},
         'TV2020': {'Town': 'TV', 'Year': 2020, 
                    'Coords': ['39, 540, 775, 40'], 
                    'Cols': ['100, 290, 315, 330, 465, 570, 620, 680, 725'],
                    'Age': 'New'},
         'TV2019': {'Town': 'TV', 'Year': 2019, 
                    'Coords': ['39, 540, 775, 40'], 
                    'Cols': ['100, 290, 315, 330, 465, 570, 620, 680, 725'],
                    'Age': 'New'},
         'TV2018': {'Town': 'TV', 'Year': 2018, 
                    'Coords': ['39, 540, 775, 40'], 
                    'Cols': ['100, 290, 315, 330, 465, 570, 620, 680, 725'],
                    'Age': 'New'},
         'TV2017': {'Town': 'TV', 'Year': 2017, 
                    'Coords': ['39, 540, 775, 40'], 
                    'Cols': ['100, 290, 315, 330, 465, 570, 620, 680, 725'],
                    'Age': 'New'},
         'TV2016': {'Town': 'TV', 'Year': 2016, 
                    'Coords': ['28, 539, 775, 42'], 
                    'Cols': ['100, 294, 315, 330, 465, 508, 570, 620, 680, 720'],
                    'Age': 'Old'},
         'TV2015': {'Town': 'TV', 'Year': 2015, 
                    'Coords': ['28, 539, 775, 42'], 
                    'Cols': ['100, 294, 315, 330, 465, 508, 570, 620, 680, 720'],
                    'Age': 'Old'},
         'TV2014': {'Town': 'TV', 'Year': 2014, 
                    'Coords': ['28, 528, 775, 42'], 
                    'Cols': ['100, 294, 315, 330, 465, 508, 570, 620, 680, 720'],
                    'Age': 'Old'}
         }

def getPgPlot(load, pg):
    # Plot a particular page of a 
    tables = camelot.read_pdf(load['Town'] + str(load['Year']) + '.pdf', 
                              flavor='stream', pages=str(pg))
    camelot.plot(tables[0], kind='text').show()
    
def tester(tables):
    # For step testing - copy newAssess function and comment out.
    cNames = {0: 'Roll Number', 1: 'Legal Address', 2: 'Tax/Exempt', 
              3: 'Prop Type Code', 4: 'Prop Type', 5:'Payer Type',
              6: 'Extra', 7: 'Land Value', 8: 'Impr. Value', 
              9: 'Other Value', 10: 'Total Value'}
    delCols = ['PrevRN', 'PrevLA', 'PrevSA', 'Extra']
    bigTab = tables[0].df.copy()
    # bigTab.drop(0, inplace=True)
    # for j in range(1, len(tables)):
    #     if tables[j].df.loc[0, 0] == 'Code  Description':
    #         continue
    #     bigTab = pd.concat([bigTab, tables[j].df.drop(0)], ignore_index=True)    
    # bigTab.rename(columns=cNames, inplace=True)
    # bigTab[['Street Address', 'Prop Subtype', 'Description']] = np.nan
    # bigTab.replace('', np.nan, inplace=True)
    # bigTab.loc[(bigTab['Legal Address'].isna()) & (~bigTab['Roll Number'].isna()),
    #             'Legal Address'] = bigTab['Tax/Exempt']
    # bigTab.loc[~bigTab['Roll Number'].isna(), 'Tax/Exempt'] = np.nan
    # bigTab['Street Address'] = bigTab['Legal Address'].shift(periods=-1)
    # bigTab['Payer Type'] = bigTab['Payer Type'].shift(periods=-1)
    # allowedPT = ['I  Individual', 'M  Municipal', 'C  Corporation', 'F  Federal',
    #               'P  Provincial']
    # bigTab.loc[~bigTab['Payer Type'].isin(allowedPT), 'Payer Type'] = np.nan
    # bigTab.loc[~bigTab['Roll Number'].isna(), 'Description'] = bigTab['Land Value']
    # bigTab['Land Value'] = bigTab['Land Value'].shift(periods=-2)
    # bigTab['Impr. Value'] = bigTab['Impr. Value'].shift(periods=-2)
    # bigTab['Other Value'] = bigTab['Other Value'].shift(periods=-2)
    # bigTab['Total Value'] = bigTab['Total Value'].shift(periods=-2)
    # bigTab['Tax/Exempt'] = bigTab['Tax/Exempt'].shift(periods=-2)
    # bigTab['Prop Type Code'] = bigTab['Prop Type Code'].shift(periods=-2)
    # bigTab['Prop Type'] = bigTab['Prop Type'].shift(periods=-2)
    # bigTab['Prop Subtype'] = bigTab['Legal Address'].shift(periods=-2)
    # bigTab.dropna(subset=['Land Value'], inplace=True)
    # bigTab['Roll Number'].ffill(inplace=True)
    # bigTab['Payer Type'].replace(['Taxable Total:', 'Exempt Total:'], np.nan, 
    #                               inplace=True)
    # bigTab['Payer Type'].ffill(inplace=True)
    # bigTab['PrevRN'] = bigTab['Roll Number'].shift(periods=1)
    # bigTab['PrevLA'] = bigTab['Legal Address'].shift(periods=1)
    # bigTab['PrevSA'] = bigTab['Street Address'].shift(periods=1)
    # bigTab.loc[bigTab['PrevRN'] == bigTab['Roll Number'], 
    #             'Legal Address'] = bigTab['PrevLA']
    # bigTab.loc[bigTab['PrevRN'] == bigTab['Roll Number'], 
    #             'Street Address'] = bigTab['PrevSA']
    # bigTab.dropna(subset=['Total Value'], inplace=True)
    # bigTab.loc[bigTab['Roll Number'].isna(), 'Legal Address'] = np.nan
    # bigTab['Legal Address'].ffill(inplace=True)
    # bigTab['Payer Type'].ffill(inplace=True)
    # bigTab['Land Value'] = bigTab['Land Value'].str.replace(',','').astype(int, errors='ignore')
    # bigTab['Impr. Value'] = bigTab['Impr. Value'].str.replace(',','').astype(int, errors='ignore')
    # bigTab['Other Value'] = bigTab['Other Value'].str.replace(',','').astype(int, errors='ignore')
    # bigTab['Total Value'] = bigTab['Total Value'].str.replace(',','').astype(int, errors='ignore')
    # bigTab['Roll Number'] = bigTab['Roll Number'].astype(int, errors='ignore')
    # bigTab.dropna(subset=['Legal Address'], inplace=True)
    # bigTab.drop(columns=delCols, inplace=True)
    # bigTab.reset_index(inplace=True, drop=True)
    # bigTab['Tax Year'] = load['Year']
    # bigTab.to_csv(load['Town'] + str(load['Year']) + '.csv', sep=',', index=False)
    return bigTab
    
def testTab(load, pg):
    # Retrieve a table object for a particular page of a particular pdf for
    # testing code.
    tables = camelot.read_pdf(load['Town'] + str(load['Year']) + '.pdf', 
                              flavor='stream', pages=str(pg), 
                              table_areas=load['Coords'], 
                              columns=load['Cols'])
    return tables

def cycle():
    for j in loads:
        print('Running ' + j)
        loads[j]['df'] = newAssess(loads[j])
        
def addTowns(load):
    fullTab = pd.DataFrame()
    for j in loads:
        newTab = pd.read_csv(load[j]['Town'] + str(load[j]['Year']) + '.csv', 
                             header=0)
        fullTab = pd.concat([fullTab, newTab], ignore_index=True)
    fullTab.to_csv(load[j]['Town'] + str(load[j]['Year']) + '.csv', sep=',', 
                   index=False)
    return