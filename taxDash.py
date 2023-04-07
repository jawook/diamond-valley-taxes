# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 07:39:03 2023

@author: wilkijam
"""

import pandas as pd
import streamlit as st
import os.path
import pathlib
import plotly_express as px

# Definitions:
dataFP = 'https://raw.githubusercontent.com/jawook/diamond-valley-taxes/main/taxRollInfo/Consolidated.csv'
currYear = 2023
sampAddress = '622 SUNRISE HILL S.W.'

# Load data:
fullSet = pd.read_csv(dataFP)

introSamp = fullSet[(fullSet['Street Address'] == sampAddress) & 
                    (fullSet['Tax Year'] <= currYear) & 
                    (fullSet['Tax Year'] >= currYear - 1)
                    ].sort_values(by=['Tax Year'])
introSamp['pctChg'] = introSamp['Total Value'].pct_change()
introCht1 = px.bar(introSamp, x='Tax Year', y='Total Value', 
                   title='Property Assessment for ' + sampAddress,
                   text='pctChg')
introCht1.update_xaxes(type='category')

intro1 = '''

This guide was created to help folks in [Diamond Valley, Alberta](https://goo.gl/maps/uzskowEQhFrGKbCG7) better understand
the process that determines property values, the mill rate and municipal tax bills
that happens each year in our community.
'''

intro2 = '''

It's March.  You just received your property assessment for the year's taxes.
Property values are up (below is a real example for my house).  That means that 
your tax bill will be higher, right?  Not so fast...
'''

taxEq1 = '''

There is one simple equation that you should know to see how property taxes 
work for municipalities.
'''

taxEq2 = '''

But that means that if property values go up, taxes go up.  Maybe...  but only
if the Mill Rate (or property tax rate that is set by town council) remains 
constant.  *You cannot determine the impact on taxes without knowing both.*
'''

st.markdown('# Taxes can be mystifying and polarizing...')
st.markdown('### ...but they don\'t have to be.')
st.markdown(intro1)
st.markdown(intro2)
st.plotly_chart(introCht1)
st.markdown(taxEq1)
st.markdown('### Assessed Value X Mill Rate = Annual Property Tax Bill')
st.markdown(taxEq2)