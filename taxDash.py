# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import streamlit as st
import plotly_express as px

# Definitions:
dataFP = 'https://raw.githubusercontent.com/jawook/diamond-valley-taxes/main/taxRollInfo/Consolidated.csv'
currYear = 2023
defaultAddr = '622 SUNRISE HILL S.W.'

# Data:

@st.cache_data
def retrData():
    fullSet = pd.read_csv(dataFP)
    return fullSet
fullSet = retrData()

@st.cache_data
def useful(fullSet):
    yearCounts = fullSet.groupby(['Roll Number', 'Tax Year']).size().unstack(fill_value=0)
    keepRolls = yearCounts[(yearCounts[currYear] > 0) & 
                           (yearCounts[currYear-1] > 0)].index
    useSet = fullSet[fullSet['Roll Number'].isin(keepRolls)]
    return useSet
useSet = useful(fullSet)

@st.cache_data
def getAddrs(useSet):
    allAddr = list(useSet['Street Address'].unique().astype(str))
    allAddr.sort()
    return allAddr
allAddr = getAddrs(useSet)

dAIdx = allAddr.index(defaultAddr)

# Sidebar loading
with st.sidebar:
    st.markdown('### START HERE: select a property for analysis')
    selAddr = st.selectbox('Street address for examples shown:', allAddr,
                           index=dAIdx)
    st.markdown('*You can type in the box above to make it easier to find ' + 
                'your address')
    st.markdown('---')
    st.markdown('*Note: if your address does not appear, it is because we do ' + 
                'not have access to 2 years of data (i.e. you live in Black Diamond')

# Data processing

introSamp = useSet[(useSet['Street Address'] == selAddr) & 
                   (useSet['Tax Year'] <= currYear) & 
                   (useSet['Tax Year'] >= currYear - 1)
                   ].sort_values(by=['Tax Year'])
introSamp['pctChg'] = introSamp['Total Value'].pct_change()

# Charts
introCht1 = px.bar(introSamp, x='Tax Year', y='Total Value', 
                   title='Property Assessment for ' + selAddr,
                   text='pctChg')
introCht1.update_xaxes(type='category')

# Multi-line text strings
tIntro1 = '''

This guide was created to help folks in [Diamond Valley, Alberta](https://goo.gl/maps/uzskowEQhFrGKbCG7) better understand
the process that determines property values, the mill rate and municipal tax bills
that happens each year in our community.

The creator is [Jamie Wilkie](mailto:jamie.c.wilkie@gmail.com).  I am a former 
1 (partial) term councillor of Turner Valley that is a self-confessed local 
politics nerd. My "real job" is as an instructor of data analysis and financial
modeling with [The Marquee Group](www.marqueegroup.ca), which was recently
acquired by Training the Street LLC. Taxes involve a lot of data. So this was a 
natural draw.
'''

tTaxEq1 = '''

---
#### Assessments are up again!  My taxes are going to skyrocket!

Maybe. But hold on a second...

There is one simple equation that you must know to understand calculation of 
property taxes for municipalities.

> ##### Assessed Value 
> ##### Times: Mill Rate 
> ##### Equals: Annual Property Tax Bill

But that means that if property values go up... **_only_**
if the Mill Rate (or property tax rate that is set by town council) remains 
constant. *You cannot determine the impact on taxes without knowing both.*

Importantly, taxes assessments are **not set by the municipality.**  Assessments
are performed by a qualified assessor that is hired by the municipality for those
purposes. More information about assessments can be found 
[at this link](http://www.municipalaffairs.alberta.ca/documents/as/ab_guideptyassmt_finrev.pdf).
'''

tMill1 = '''
---

#### So how does the mill rate get calculated?

But towns can set the mill rate at whatever they want to make sure that my taxes
always go up, right? Sort of. The mill rate is a simple mechanical calculation. 
The municipality creates a budget every year. The town takes all of the costs for 
the year and deducts all other sources of financing (like grants from provincial
or federal governments) and that is the total amount of municipal spending that
must be raised via taxes.  So one more equation, but it's not that tough.

> ##### Total Municipal Expenses 
> ##### Minus: Grants, Reserve Usasge and Other Non-Tax Revenue 
> ##### Equals: Amount to be Raised by General Municipal Tax

After that, the town adds up all of the assessed values of property in town and takes
the total amount needed and divides it by the total assessed value. That's the mill rate.
Thats's all there is to it!

*Note: there is one minor complication, municipalities will typically set a different
mill rate for businesses and for residences.  However, the above holds for the
municipality as a whole.*
'''

tWhyAssess = '''

---
#### So what is the point of the assessment? 

Assessment exist exclusiveliy to determine what *your home's share* of the total 
municipal tax levied. If the amount of expenses for the municipality stay the same,
and the total overall assessment stays the same, the mill rate will stay the same.
But your individual tax bill will depend on how your assessment changes *relative
to all other assessments in the community.*

As an example, if the total amount to be raised by general municipal taxes stayed
the same year-over-year, but your house value increased and every other house 
decreased in value, your annual tax bill would go up (and everyone else's would
go down slightly).

So how did your change in assessment compare to other's?

'''

# mainapp configuration
st.image('animation.gif')
st.markdown(tIntro1)
st.plotly_chart(introCht1)
st.markdown(tTaxEq1)
st.markdown(tMill1)
st.markdown(tWhyAssess)