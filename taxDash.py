# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import streamlit as st
import plotly_express as px

# Definitions:
dataFP = 'https://raw.githubusercontent.com/jawook/diamond-valley-taxes/main/taxRollInfo/Consolidated.csv'
currYear = 2023
defaultAddr = '622 SUNRISE HILL S.W.'
defColors = px.colors.qualitative.Vivid

#%% Data retrieval

@st.cache_data
def retrData():
    fullSet = pd.read_csv(dataFP)
    return fullSet
fullSet = retrData()

#%% Data processing functions

@st.cache_data
def useful(fullSet, currYear):
    yearCounts = fullSet.groupby(['Roll Number', 'Tax Year']).size().unstack(fill_value=0)
    keepRolls = yearCounts[(yearCounts[currYear] > 0) & 
                           (yearCounts[currYear-1] > 0)].index
    useSet = fullSet[fullSet['Roll Number'].isin(keepRolls)]
    useSet = useSet[(useSet['Prop Type Code']=='2') & 
                    (useSet['Tax/Exempt']=='T')]
    return useSet
useSet = useful(fullSet, currYear)

def getYoYChng(useSet, currYear):
    wideSet = pd.pivot_table(useSet, index='Roll Number', 
                             columns='Tax Year', values='Total Value', 
                             aggfunc=np.sum)
    wideSet = pd.merge(left=wideSet, 
                        right=useSet[['Roll Number', 'Street Address']].drop_duplicates(subset=['Roll Number'], keep='first'),
                        how='left', on='Roll Number')
    wideSet = wideSet[['Street Address', currYear, currYear - 1]]
    wideSet['dolChg'] = wideSet[currYear] - wideSet[currYear - 1]
    wideSet['pctChg'] = (wideSet[currYear] / wideSet[currYear - 1]) - 1
    wideSet.dropna(how='any', inplace=True)
    return wideSet
YoYChng = getYoYChng(useSet, currYear)

def getDistnData(useSet):
    distnData = useSet[['Roll Number', 'Total Value', 'Tax Year']]
    return distnData
distnData = getDistnData(useSet)

@st.cache_data
def getAddrs(useSet):
    allAddr = list(useSet['Street Address'].unique().astype(str))
    allAddr.sort()
    return allAddr
allAddr = getAddrs(useSet)
dAIdx = allAddr.index(defaultAddr)

#%% Sidebar loading
with st.sidebar:
    st.markdown('### START HERE: select a property for analysis')
    selAddr = st.selectbox('Street address for examples shown:', allAddr,
                           index=dAIdx)
    st.markdown('You can type in the box above to make it easier to find ' + 
                'your address')
    st.markdown('---')
    st.markdown('*Note: if your address does not appear, it is because we do ' + 
                'not have access to 2 years of data (i.e. you live in Black Diamond' +
                'and we haven\'t been able to get that data*')

#%% post-selection data processing
@st.cache_data
def getIntroSamp(useSet, currYear):
    introSamp = useSet[(useSet['Street Address'] == selAddr) & 
                       (useSet['Tax Year'] <= currYear) & 
                       (useSet['Tax Year'] >= currYear - 1)
                       ].sort_values(by=['Tax Year'])
    introSamp['pctChg'] = introSamp['Total Value'].pct_change()
    return introSamp
introSamp = getIntroSamp(useSet, currYear)

#%% variable calculation

sampPx2 = introSamp.loc[introSamp['Tax Year']==currYear, ['Total Value']].values[0][0]
sampPx1 = introSamp.loc[introSamp['Tax Year']==currYear-1, ['Total Value']].values[0][0]
sampYoY = introSamp.loc[introSamp['Tax Year']==currYear, ['pctChg']].values[0][0]
y1Avg = distnData[(distnData['Tax Year']==currYear)]['Total Value'].mean()
y2Avg = distnData[(distnData['Tax Year']==(currYear-1))]['Total Value'].mean()

#%% charts
## single property yoy chng
introCht1 = px.bar(introSamp, x='Tax Year', y='Total Value', 
                   title='Property Assessment for<br>' + selAddr.title(),
                   color_discrete_sequence=defColors)
introCht1.update_xaxes(type='category')
introCht1.update_yaxes(visible=False)
introCht1.add_annotation(x=1, y=sampPx2, 
                         text='<b>{:+.1%}</b>'.format(sampYoY),
                         showarrow=False, yshift=10, font=dict(color=defColors[0]))
introCht1.add_annotation(x=0, y=sampPx1, 
                         text='<b>${:,.0f}</b>'.format(sampPx1),
                         showarrow=False, yshift=-10, font=dict(color='white'))
introCht1.add_annotation(x=1, y=sampPx2, 
                         text='<b>${:,.0f}</b>'.format(sampPx2),
                         showarrow=False, yshift=-10, font=dict(color='white'))

## distribution yoy
introCht2 = px.histogram(distnData[(distnData['Tax Year']==currYear)|
                                   (distnData['Tax Year']==(currYear-1))], 
                         x='Total Value', color='Tax Year',
                         barmode='overlay', color_discrete_sequence=defColors,
                         nbins=20, 
                         title='Distribution of Residential<br>Property ' + 
                         'Assessments')
introCht2.add_annotation(x=y1Avg, y=225, showarrow=False, text="<b>" + str(currYear) + 
                         ' Avg: </b><br>${:,.0f} </b><br>'.format(y1Avg) + 
                         '{b:+,.0%}'.format(b=(y1Avg/y2Avg)-1), xshift=50, 
                         font=dict(color=defColors[0]))
introCht2.add_vline(x=y1Avg, line_width=3, line_dash='dash', line_color=defColors[0])
introCht2.add_annotation(x=y2Avg, y=225, showarrow=False, text="<b>" + str(currYear - 1) + 
                         ' Avg: </b><br>${a:,.0f}<br> '.format(a=y2Avg), xshift=-50, 
                         font=dict(color=defColors[1]))
introCht2.add_vline(x=y2Avg, line_width=3, line_dash='dash', line_color=defColors[1])
introCht2.update_xaxes(title='Residential Property Value', tickformat='$,.0f')
introCht2.update_yaxes(title='Number of Properties')

# yoyChg charts ($ change)
yoyCht1 = px.bar(YoYChng.sort_values(by='dolChg', ascending=True), x ='dolChg',
                 y ='Street Address')
yoyCht1.update_yaxes(visible=False)

# Multi-line text strings
tIntro1 = '''

This guide was created to help folks in [Diamond Valley, Alberta](https://goo.gl/maps/uzskowEQhFrGKbCG7) better understand
the process that determines property values, the mill rate and municipal tax bills
that happens each year in our community.

The creator is [Jamie Wilkie](mailto:jamie.c.wilkie@gmail.com).  I was briefly
a councillor of Turner Valley and am a self-confessed local 
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

> ##### Amount to be Raised by General Municipal Tax
> ##### Divided by: Total Property Assessment
> ##### Equals: Mill Rate

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
introChts1, introChts2 = st.columns(2)
with introChts1:
    st.plotly_chart(introCht1, use_container_width=True, 
                    config = {'displayModeBar': False})
with introChts2:
    st.plotly_chart(introCht2, use_container_width=True,
                    config = {'displayModeBar': False})
st.markdown(tTaxEq1)
st.markdown(tMill1)
st.markdown(tWhyAssess)
yoyChts1, yoyChts2 = st.columns(2)
with yoyChts1:
    st.plotly_chart(yoyCht1, use_container_width=True,
                    config = {'displayModeBar': False})
