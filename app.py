#Required Libraries
#import altair as alt
#import datapane as dp
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st  # 🎈 data web app development

#Reading the data from JHU github
url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
df = pd.read_csv(url)

#required variables
date_columns = list(df.columns[4:])

#%%timeit -r1 -n1
df_final = pd.DataFrame()
pd.set_option('display.float_format', lambda x: '%.3f' % x)
for value, country in enumerate( list(df['Country/Region'].unique())):
#for value, country in enumerate(countries):
    df_grouped = (
     df.query("`Country/Region` == @country") \
     .melt(id_vars = ['Country/Region'], value_vars = date_columns, var_name = 'date', value_name = "infected_cases")
    )
    
    df_final = pd.concat([df_final,(df_grouped.groupby(pd.PeriodIndex(df_grouped['date'], freq="W"))['infected_cases'].mean().reset_index()\
                        .assign(country = country)
                        .assign(start_week = lambda df_grouped : df_grouped['date'].astype('str').str.split('/').str[0].astype('datetime64[ns]')) \
                        .assign(end_week = lambda df_grouped : df_grouped['date'].astype('str').str.split('/').str[1].astype('datetime64[ns]')) \
                        .iloc[:,1:]
             )]) 
    #print(df_final.shape)

top10= list(df_final[['start_week', 'country', 'infected_cases']].sort_values(by = ['start_week', 'infected_cases'], ascending = [False, False]).head(10)['country'].unique())
#countries = list(df['Country/Region'].unique())  

st.set_page_config(
    page_title="Hourly worldwide John hopkins based covid update",
    page_icon="✅",
    layout="wide",
)
st.title("Covid19 Worldwide Dashboard")

placeholder = st.empty()

# create two columns for charts
fig_col1, fig_col2, fig_col3 = st.columns(3)

with fig_col1:
    st.markdown("### First Chart")
    fig = px.density_heatmap(
        data_frame=df_final.query('country.isin(@top10)'), y="infected_cases", x="country"
    )
    st.write(fig)
   
with fig_col2:
    st.markdown("### Second Chart")
    fig2 = px.histogram(data_frame=df_final.query('country.isin(@top10)'), x="infected_cases")
    st.write(fig2)
    
with fig_col3:
    st.markdown("### Third Chart")
    fig3 = px.line(df_final.query('country.isin(@top10)'), x="start_week", y="infected_cases", color = 'country',
                  markers=False,
               labels={
                     "start_week": "Month-Year",
                     "infected_cases": "Infected Cases(Millions)"                    
                 },
                title="Cumalative Weekly Avg Infected Cases Worldwide"
              )
    st.write(fig3)

st.markdown("### Detailed Data View")
st.dataframe(df_final)

