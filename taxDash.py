# -*- coding: utf-8 -*-

# TODO NOTES
# Next chart should show distribution of tax changes (both % and dollar??? side by side?)
# hoverformats need to be set for all charts

import pandas as pd
import numpy as np
import streamlit as st
import plotly_express as px
import re

# Definitions:
rollFP = 'taxRollInfo/Consolidated.csv'
millFP = 'taxRateData/taxRates.csv'
currYear = 2023
defaultAddr = '622 Sunrise Hill S.W.'
defColors = px.colors.qualitative.G10
problemAddrs = ['1000 Oakalta Road Nw', '1000 Oakalta Road S.W.']

#%% Data retrieval

@st.cache_data
def retrRoll(fp):
    fullSet = pd.read_csv(fp)
    fullSet['Street Address'] = fullSet['Street Address'].str.title()
    return fullSet
fullSet = retrRoll(rollFP)

@st.cache_data
def retrRate(fp):
    rates = pd.read_csv(fp)
    return rates
rates = retrRate(millFP)

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

@st.cache_data
def getYoYChng(useSet, currYear):
    wideSet = pd.pivot_table(useSet, index='Roll Number', 
                             columns='Tax Year', values='Total Value', 
                             aggfunc=np.sum)
    wideSet = pd.merge(left=wideSet,
                       right=useSet[['Roll Number', 'Street Address', 'Town']].drop_duplicates(subset=['Roll Number'], 
                                                                                        keep='last'),
                       how='left', on='Roll Number')
    wideSet = wideSet[['Street Address', 'Town', currYear, currYear - 1]]
    wideSet['dolChg'] = wideSet[currYear] - wideSet[currYear - 1]
    wideSet['pctChg'] = (wideSet[currYear] / wideSet[currYear - 1]) - 1
    wideSet.dropna(how='any', inplace=True)
    return wideSet
YoYChng = getYoYChng(useSet, currYear)

@st.cache_data
def getDistnData(useSet):
    distnData = useSet[['Roll Number', 'Total Value', 'Tax Year']]
    return distnData
distnData = getDistnData(useSet)

@st.cache_data
def getAddrs(df):
    allAddr = list(df['Street Address'].unique().astype(str))
    allAddr.sort()
    return allAddr

@st.cache_data
def getTaxCalcs(useSet, currYear, rates):
    taxTbl = getYoYChng(useSet, currYear)
    rates = rates[(rates['Tax Year']==(currYear-1)) & 
                  (rates['Category']=='Residential') &
                  (rates['Type']=='General Municipality')]
    taxTbl = pd.merge(left=taxTbl, right=rates, how='left', on='Town')
    taxTbl.drop(columns=['Category', 'Type', 'Tax Year'], inplace=True)
    taxTbl['y1MTax'] = taxTbl[currYear-1] * (taxTbl['Rate'] / 1000)
    taxTbl['y2MTaxFlat'] = taxTbl[currYear] * (taxTbl['Rate'] / 1000)
    taxTbl['yoyTaxFlat'] = taxTbl['y2MTaxFlat'] - taxTbl['y1MTax']
    taxTbl['yoyTaxFlatPct'] = (taxTbl['yoyTaxFlat'] / taxTbl['y1MTax'])
    taxTbl.sort_values(by='yoyTaxFlat', inplace=True)
    return taxTbl
taxTbl = getTaxCalcs(useSet, currYear, rates)

allAddr = getAddrs(useSet)
for j in problemAddrs:
    allAddr.remove(j)
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
                ' where we haven\'t been able to get that data yet). ' + 
                'If you have suggestions or questions or find errors, feel free '+
                'to reach out to [Jamie Wilkie](mailto:jamie.c.wilkie@gmail.com).*')

#%% post-selection data processing
@st.cache_data
def getIntroSamp(useSet, currYear, selAddr):
    introSamp = useSet[(useSet['Street Address'] == selAddr) & 
                       (useSet['Tax Year'] <= currYear) & 
                       (useSet['Tax Year'] >= currYear - 1)
                       ].sort_values(by=['Tax Year'])
    introSamp['pctChg'] = introSamp['Total Value'].pct_change()
    return introSamp
introSamp = getIntroSamp(useSet, currYear, selAddr)

@st.cache_data
def getTaxSamp(useSet, currYear, selAddr, rates):
    taxSamp = useSet[(useSet['Street Address'] == selAddr) &
                     (useSet['Tax Year'] <= currYear) &
                     (useSet['Tax Year'] >= currYear - 1)
                     ].sort_values(by=['Tax Year'])
    taxSamp = pd.merge(left=taxSamp, 
                       right=rates[(rates['Category'] == 'Residential') &
                                   (rates['Type'] == 'General Municipality')], 
                       how='left', on=['Town', 'Tax Year'])
    taxSamp['flatRate'] = taxSamp['Rate'].ffill()
    taxSamp['flatTax'] = taxSamp['Total Value'] * (taxSamp['flatRate'] / 1000)
    return taxSamp
taxSamp = getTaxSamp(useSet, currYear, selAddr, rates)

#%% used functions

def closest(serLst, retLst, K):
    serLst = np.asarray(serLst)
    retLst = np.asarray(retLst)
    idx = (np.abs(serLst-K)).argmin()
    return retLst[idx]

#%% variable calculation

# for introCht1
sampPx2 = introSamp.loc[introSamp['Tax Year']==currYear, ['Total Value']].values[0][0]
sampPx1 = introSamp.loc[introSamp['Tax Year']==currYear-1, ['Total Value']].values[0][0]
sampYoY = introSamp.loc[introSamp['Tax Year']==currYear, ['pctChg']].values[0][0]
sampYoYDol = sampPx2 - sampPx1

# for yoyCht1
yoyAvgDol = YoYChng['dolChg'].mean()
yoyClsDol = closest(YoYChng['dolChg'], YoYChng['Street Address'], yoyAvgDol)
yoyAvgPct = YoYChng['pctChg'].mean()
yoyClsPct = closest(YoYChng['pctChg'], YoYChng['Street Address'], yoyAvgPct)

# for taxCht1
y2Avg = distnData[(distnData['Tax Year']==currYear)]['Total Value'].mean()
y1Avg = distnData[(distnData['Tax Year']==(currYear-1))]['Total Value'].mean()
y1Tax = taxSamp.loc[taxSamp['Tax Year']==(currYear-1), ['flatTax']].values[0][0]
y2TaxFlat = taxSamp.loc[taxSamp['Tax Year']==currYear, ['flatTax']].values[0][0]
pctTaxFlat = y2TaxFlat / y1Tax - 1
dolTaxFlat = y2TaxFlat - y1Tax

# for taxCht2
y1TotalTax = taxTbl['y1MTax'].sum()
y2TotalTaxFlat = taxTbl['y2MTaxFlat'].sum()
yoyTaxDolAvgFlat = taxTbl['yoyTaxFlat'].mean()
yoyTaxPctAvgFlat = taxTbl['yoyTaxFlatPct'].mean()
sampYoyTaxDolFlat = taxTbl.loc[taxTbl['Street Address']==selAddr, ['yoyTaxFlat']].values[0][0]
sampYoyTaxPctFlat = taxTbl.loc[taxTbl['Street Address']==selAddr, ['yoyTaxFlatPct']].values[0][0]
yoyClsTaxPctAvgFlat = closest(taxTbl['yoyTaxFlatPct'], taxTbl['Street Address'], yoyTaxPctAvgFlat)
yoyClsTaxDolAvgFlat = closest(taxTbl['yoyTaxFlat'], taxTbl['Street Address'], yoyTaxDolAvgFlat)

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
                         text='<b>' + 
                         '${:,.0f}</b>'.format(sampPx1),
                         showarrow=False, yshift=-10, font=dict(color='white'))
introCht1.add_annotation(x=1, y=sampPx2, 
                         text='<b>' + 
                         '${:,.0f}</b>'.format(sampPx2),
                         showarrow=False, yshift=-10, font=dict(color='white'))

## distribution yoy
introCht2 = px.histogram(distnData[(distnData['Tax Year']==currYear)|
                                   (distnData['Tax Year']==(currYear-1))], 
                         x='Total Value', color='Tax Year',
                         barmode='overlay', color_discrete_sequence=defColors,
                         nbins=20, 
                         title='Distribution of Residential<br>Property ' + 
                         'Assessments')
introCht2.add_annotation(x=y2Avg, y=225, showarrow=False, text="<b>" + str(currYear) + 
                         ' Avg: </b><br>${:,.0f} </b><br>'.format(y2Avg) + 
                         '{b:+,.0%}'.format(b=(y2Avg/y1Avg)-1), xshift=50, 
                         font=dict(color=defColors[0]))
introCht2.add_vline(x=y2Avg, line_width=3, line_dash='dash', line_color=defColors[0])
introCht2.add_annotation(x=y1Avg, y=225, showarrow=False, text="<b>" + str(currYear - 1) + 
                         ' Avg: </b><br>${a:,.0f}<br> '.format(a=y1Avg), xshift=-50, 
                         font=dict(color=defColors[1]))
introCht2.add_vline(x=y1Avg, line_width=3, line_dash='dash', line_color=defColors[1])
introCht2.update_xaxes(title='Residential Property Value', tickformat='$,.0f')
introCht2.update_yaxes(title='Number of Properties')

# yoyChg charts ($ change)
yoyCht1 = px.bar(YoYChng.sort_values(by='dolChg', ascending=True), x ='dolChg',
                 y ='Street Address', color_discrete_sequence=defColors,
                 title='$ Change in Assessed Value from ' + str(currYear-1) +
                 ' - ' + str(currYear))
yoyCht1.update_xaxes(title='Change in Property Assessment ($000s)', 
                     tickformat='$~s', range=[0,100000])
yoyCht1.add_hline(y=selAddr, line_width=3, line_dash='dash', line_color=defColors[2])
yoyCht1.add_annotation(text='<b>' + selAddr + ': ' + 
                       re.sub(r'[0-9,.]','','{a:+0f}'.format(a=sampYoYDol)) + 
                       '${:,.0f}</b>'.format(sampYoYDol), 
                       y=selAddr, showarrow=False, yshift=10,
                       font=dict(color=defColors[2]))
yoyCht1.add_hline(y=yoyClsDol, line_width=3, line_dash='dash', line_color=defColors[6])
yoyCht1.add_annotation(text='<b>Avg. Change: ' + 
                       re.sub(r'[0-9,.]','','{a:+0f}'.format(a=yoyAvgDol)) + 
                       '${:,.0f}</b>'.format(yoyAvgDol), 
                       y=yoyClsDol, showarrow=False, yshift=-10,
                       font=dict(color=defColors[6]))
yoyCht1.update_yaxes(visible=False)


# yoyChg charts (% change)
yoyCht2 = px.bar(YoYChng.sort_values(by='pctChg', ascending=True), x ='pctChg',
                 y ='Street Address', color_discrete_sequence=defColors,
                 title='% Change in Assessed Value from ' + str(currYear-1) +
                 ' - ' + str(currYear))
yoyCht2.update_xaxes(title='% Change in Property Assessment', 
                     tickformat='.1%', range=[0,0.4])
yoyCht2.add_hline(y=selAddr, line_width=3, line_dash='dash', line_color=defColors[2])
yoyCht2.add_annotation(text='<b>' + selAddr + ': {:+,.1%}</b>'.format(sampYoY), 
                       y=selAddr, showarrow=False, yshift=10,
                       font=dict(color=defColors[2]))
yoyCht2.add_hline(y=yoyClsPct, line_width=3, line_dash='dash', line_color=defColors[6])
yoyCht2.add_annotation(text='<b>Avg. Change: {:+,.1%}</b>'.format(yoyAvgPct), 
                       y=yoyClsPct, showarrow=False, yshift=-10,
                       font=dict(color=defColors[6]))
yoyCht2.update_yaxes(visible=False)


# yoy Tax Change
taxCht1 = px.bar(taxSamp, x='Tax Year', y='flatTax', 
                 title='Municipal Taxes for ' + str(selAddr) + 
                 '<br>(Assuming a Flat Mill Rate in ' + str(currYear) + ')',
                 color_discrete_sequence=defColors)
taxCht1.update_xaxes(type='category')
taxCht1.update_yaxes(tickformat='$,.0f', visible=False)
taxCht1.add_annotation(x=0, y=y1Tax, 
                       text='<b>${a:,.0f}</b>'.format(a=y1Tax),
                       showarrow=False, yshift=-10, font=dict(color='white'))
taxCht1.add_annotation(x=1, y=y2TaxFlat, 
                       text='<b>${a:,.0f}</b>'.format(a=y2TaxFlat),
                       showarrow=False, yshift=-10, font=dict(color='white'))
taxCht1.add_annotation(x=1, y=y2TaxFlat, 
                       text='<b>{a:+,.1%}</b><br>{b:+,.0f}'.format(a=pctTaxFlat, b=dolTaxFlat),
                       showarrow=False, yshift=20, font=dict(color=defColors[0]))


# yoy Tax Change distribution
taxCht2 = px.bar(taxTbl, x='yoyTaxFlat', 
                 y='Street Address', title='Distribution of YoY Change in Taxes <br>'+ 
                 '(Assuming a Flat Mill Rate in ' + str(currYear)+ ')')
taxCht2.add_annotation(y=selAddr, x=400, showarrow=False, 
                       text="<b>" + str(selAddr) + ': ' +
                       re.sub(r'[0-9,.]','','{a:+0f}'.format(a=sampYoyTaxDolFlat)) + 
                       '${b:,.0f}'.format(b=sampYoyTaxDolFlat), 
                       yshift=10, font=dict(color=defColors[6]))
taxCht2.add_hline(y=selAddr, line_width=3, line_dash='dash', line_color=defColors[6])
taxCht2.add_annotation(y=yoyClsTaxDolAvgFlat, x=400, showarrow=False, 
                       text="<b>" + str(currYear - 1) + '->' + str(currYear) +
                       ' Avg: ' + re.sub(r'[0-9,.]','','{a:+0f}'.format(a=yoyTaxDolAvgFlat)) +
                       '${a:,.0f}'.format(a=yoyTaxDolAvgFlat), yshift=-10, 
                       font=dict(color=defColors[2]))
taxCht2.add_hline(y=yoyClsTaxDolAvgFlat, line_width=3, line_dash='dash', line_color=defColors[2])
taxCht2.update_yaxes(visible=False)
taxCht2.update_xaxes(range=[0, 801], tickformat='$,.0f',
                     title='Change in Taxes from ' + str(currYear - 1) + '->' + 
                     str(currYear))




#%% Multi-line text strings
tIntro1 = '''

This guide was created to help folks in [Diamond Valley, Alberta](https://goo.gl/maps/uzskowEQhFrGKbCG7) better understand
the process that determines property values, the mill rate and municipal tax bills
that happens each year in our community.

I'm the creator, [Jamie Wilkie](mailto:jamie.c.wilkie@gmail.com).  I was briefly
a councillor of Turner Valley and am a self-confessed local 
politics nerd. My "real job" is as an instructor of data analysis and financial
modeling with [The Marquee Group](www.marqueegroup.ca), which was recently
acquired by Training the Street LLC. 

Taxes involve a lot of data. So this was a natural draw.

---
#### Assessments are up again!  My taxes are going to skyrocket!
'''

tTaxEq1 = '''
Maybe. But hold on a second...

There is one simple equation that you must know to understand property taxes 
for municipalities.

> ##### Assessed Value 
> ##### Times: Mill Rate 
> ##### Equals: Annual Property Tax Bill

But that means that when property values go up, taxes increase **_only_**
if the Mill Rate (or property tax rate that is set by town council) remains 
constant. *You cannot determine the impact on taxes without knowing both.*

Importantly, tax assessments are **not set by the municipality.**  Assessments
are performed by a qualified assessor that is hired by the municipality for those
purposes. More information about assessments can be found 
[at this link](http://www.municipalaffairs.alberta.ca/documents/as/ab_guideptyassmt_finrev.pdf).
'''

tMill1 = '''
---

#### So I need to know the mill rate, how is that calculated?

Towns can set the mill rate at whatever they want to make sure that my taxes
always go up, right? Sort of. The mill rate is a simple mechanical calculation. 
The municipality creates a budget every year. The town takes all of the costs for 
the year and deducts all other sources of financing (like grants from provincial
or federal governments) and that is the total amount of municipal spending that
must be raised via taxes.  So two more equations (I know, I lied about there only 
being one), but it's not that tough.

> ##### Total Municipal Expenses 
> ##### Minus: Grants, Reserve Usasge and Other Non-Tax Revenue 
> ##### Equals: Amount to be Raised by General Municipal Tax

After that, the town adds up all of the assessed values of property in town and takes
the total amount to be raised and divides it by the total assessed value. That's 
the mill rate. Thats's all there is to it!

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

So how did your change in assessment compare to others?

'''

tSoWhat1 = '''
---
#### So what does this mean for my tax bill?

What most people are concerned about if assessments increase, is that tax bills
will go up by the same % amount.  And that is true if council holds the mill rate
flat.  So lets see what that would look like:

'''

tSoWhat2 = '''
---
But this assumes that your mill rate stays flat.  Like that is some sort of default
position.  **That should never be the default position!**  The mill rate is a simple 
calculation -- not a "rate" that needs to be targetted.

If the mill rate stays the same, while property assessments increase by, on average,
{a:,.1%}, that would mean that the town would be collecting (and spending!) an 
additional {a:,.1%} in residential taxes.  

The question would be, why?  Why would town spending need to increase the same 
amount as property values increase?

Instead, let\'s ask, how much extra (or less) is reasonable for an increase to the 
amount of taxes required on a year-over-year basis (assuming there is no growth 
in households).  There are a lot of factors that should go into that answer:

- Wage, service & material inflation
- Costs of amalgamation
- Additional services offered
- Service reductions
- Amalgamation efficiencies
- Reductions/increases to grant availability
- Costs downloaded to municipalities from other levels of government

So -- why don\'t you pick?

'''

tSoWhat3 = '''

So, in short, the material driver of changes in your property taxes is the budget
less grants and other non-tax sources of revenue. To be precise, the figure that 
needs to be watched is that number *per household.*  

And even if that number is flat, your tax bill may change based on the relative 
change in your assessment (i.e. if your property increases in value more than 
other properties, your tax bill will go up and others will go down).

The reality is, the mill rate means nothing without knowing the change in 
assessments.  And assessments mean nothing without the mill rate.  Neither of them
matter much unless you know **the budget per household less grants and other non-tax
sources of revenue.**

I hope this helps to make things more clear to people.  It\'s a lot, I understand
that. But it is critically important to understand if you want to know how your
tax bill works!
'''

tWrapUp1 = '''
---
#### Final Thoughts

If you have suggestions or questions or find errors, feel free to reach out to 
[Jamie Wilkie](mailto:jamie.c.wilkie@gmail.com).

If you are interested in seeing how this data was compiled, and want to play 
around with the original data, all code and source files can be found at this 
[github repository](https://github.com/jawook/diamond-valley-taxes).

The code to collect, shape & analyze data was written in [python](https://www.python.org/). 
[Streamlit](https://streamlit.io/) was used to put together this interactive app. [Plotly](https://plotly.com/) 
is used for the visualizations.

'''

#%% mainapp configuration
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
with yoyChts2:
    st.plotly_chart(yoyCht2, use_container_width=True,
                    config = {'displayModeBar': False})
st.markdown(tSoWhat1)
soWhat1, soWhat2 = st.columns(2)
with soWhat1:
    st.plotly_chart(taxCht1, use_container_width=True,
                    config = {'displayModeBar': False})
with soWhat2:
    st.plotly_chart(taxCht2, use_container_width=True,
                    config = {'displayModeBar': False})
st.markdown(tSoWhat2.format(a=yoyAvgPct))
costIncr = st.slider('Selected cost base increase / (decrease):', -20.0, 
                     20.0, 0.0, 0.5, '%.1f%%')

#%% intermission calculations based on slider selection
y2TotalUPik = y1TotalTax * (1 + (costIncr/100))
y2TotalAssess = taxTbl[currYear].sum()
y2RateUPik = (y2TotalUPik / y2TotalAssess) * 1000
y1Rate = taxTbl.loc[taxTbl['Street Address']==selAddr]['Rate'].values[0]
taxTbl['y2RateUPik'] = y2RateUPik
taxTbl['y2MTaxUPik'] = (taxTbl['y2RateUPik'] / 1000) * taxTbl[currYear]
taxTbl['yoyTaxUPik'] = taxTbl['y2MTaxUPik'] - taxTbl['y1MTax']
taxTbl['yoyTaxUPikPct'] = taxTbl['yoyTaxUPik'] / taxTbl['y1MTax']
taxTbl.sort_values(by='yoyTaxUPik', inplace=True)
sampY1MTax = taxTbl.loc[taxTbl['Street Address']==selAddr]['y1MTax'].values[0]
sampY2MTaxUPik = taxTbl.loc[taxTbl['Street Address']==selAddr]['y2MTaxUPik'].values[0]
yoyDolSampUPik = sampY2MTaxUPik - sampY1MTax
yoyPctSampUPik = yoyDolSampUPik / sampY1MTax
millSampUPik = pd.DataFrame({'Year': [currYear-1, currYear], 
                             'Mill': [y1Rate, y2RateUPik]})
yoyDolAvgUPik = taxTbl['yoyTaxUPik'].mean()
yoyClsDolAvgUPik = closest(taxTbl['yoyTaxUPik'], taxTbl['Street Address'], yoyDolAvgUPik)
rngDolTaxUPik = taxTbl['yoyTaxUPik'].quantile([.01, .99])

#%% intermission charts based on slider selection

# yoy Tax Change
taxCht3 = px.bar(millSampUPik, x='Year', y='Mill', 
                 title='<b>Mill Rate Assuming a ' + '{:+.1%}'.format(costIncr/100) + 
                 '<br>Change in Amount to be Raised by Municipal Tax',
                 color_discrete_sequence=defColors, text='Mill',
                 text_auto='.5f')
taxCht3.update_xaxes(type='category')
taxCht3.update_yaxes(tickformat='$,.0000f', visible=False)
taxCht3.update_traces(textposition='outside')


# yoy Tax Change distribution
taxCht4 = px.bar(taxTbl, x='yoyTaxUPik', 
                  y='Street Address', title='Distribution of YoY Change in Taxes <br>'+ 
                  '(Assuming Mill Rate Seen to the Left)')
taxCht4.add_annotation(y=selAddr, x=rngDolTaxUPik.mean(), showarrow=False, 
                        text="<b>" + str(selAddr) + ': ' +
                        re.sub(r'[0-9,.]','','{a:+0f}'.format(a=yoyDolSampUPik)) + 
                        re.sub(r'[-]', '', '${b:,.0f}'.format(b=yoyDolSampUPik)), 
                        yshift=10, font=dict(color=defColors[6]))
taxCht4.add_hline(y=selAddr, line_width=3, line_dash='dash', line_color=defColors[6])
taxCht4.add_annotation(y=yoyClsDolAvgUPik, x=rngDolTaxUPik.mean(), showarrow=False, 
                        text="<b>" + str(currYear - 1) + '->' + str(currYear) +
                        ' Avg: ' + re.sub(r'[0-9,.]','','{a:+0f}'.format(a=yoyDolAvgUPik)) +
                        '${a:,.0f}'.format(a=yoyDolAvgUPik), yshift=-10, 
                        font=dict(color=defColors[2]))
taxCht4.add_hline(y=yoyClsDolAvgUPik, line_width=3, line_dash='dash', line_color=defColors[2])
taxCht4.update_yaxes(visible=False)
taxCht4.update_xaxes(range=rngDolTaxUPik, tickformat='$,.0f',
                      title='Change in Taxes from ' + str(currYear - 1) + '->' + 
                      str(currYear))

#%% mainapp continued
soWhat3, soWhat4 = st.columns(2)
with soWhat3:
    st.plotly_chart(taxCht3, use_container_width=True,
                    config = {'displayModeBar': False})
with soWhat4:
    st.plotly_chart(taxCht4, use_container_width=True,
                    config = {'displayModeBar': False})
st.markdown(tSoWhat3)
st.markdown(tWrapUp1)