*Prepared by: [Jamie Wilkie](mailto:jamie.c.wilkie@gmail.com)* 

*[Interactive dashboard link](LINK TO BE CREATED)*

# Diamond Valley Tax Analysis

Every year there is confusion and concern about the determination and calculation of municipal taxes.  As a result, I wanted to put together a tool that will help people to understand their taxes a little better so that people are better able to understand the calculation and cut through misinformation and "spin".

## Data Sources
All data is sourced from publicly available information.  Currently, the [old Turner Valley website](https://turnervalley.ca/services/municipal-services/assessments/) publishes historical assessment information going back to 2014.  Additionally, the initial 2023 tax assessment roll (a listing of all property tax assessments in the community) has been posted to [the Diamond Valley website](https://www.diamondvalley.town/153/Property-Assessments).  All pdf files have been downloaded to this github repo for posterity.

On March 29, 2023, I requested spreadsheet versions of these files by email to the [Diamond Valley tax email address](mailto:tax@diamondvalley.town "Link to send email to Diamond Valley tax department").  As of April 3, 2023, I have not received that information.  I will update if the information is made availabile.  

Unfortunately this meant that I needed to create a program to parse the pdf files and extract all relevant information.  This was done using Python and the script is [available here](LINK TO BE CREATED). The creation requires the libraries pandas and camelot-py, which you can get from your favorite library repos.

In addition, information for Black Diamond properties prior to 2023 taxation year was **not available** as of this date.  I also requested this information for a similar timeframe and will post an update if it is made available.

As a result, I created a master dataset in csv format that is [available here](LINK TO BE CREATED). I'm an amateur coder, and make no representations about the perfection of this data, if you notice any errors, please feel free to [send me a message](mailto:jamie.c.wilkie@gmail.com)!

## Analysis
After aggregation of all data, the dashboard that you [see here](LINK TO BE CREATED) was created [using Streamlit](https://streamlit.io/).  The code for the dashboard can be [found here](LINK TO BE CREATED).  If you have any comments, questions or suggestions, please reach out.
