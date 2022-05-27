import streamlit as st
import pandas as pd
from urllib.request import urlopen
import ssl
import certifi
import json
import plotly.express as px
from dateutil import rrule

## Path variables to all data files
covid_confirmed_usafacts ='/Users/anujkawane/Desktop/DataCopy/covid_confirmed_usafacts.csv'
covid_deaths_usafacts = '/Users/anujkawane/Desktop/DataCopy/covid_deaths_usafacts.csv'
covid_county_population_usafacts = '/Users/anujkawane/Desktop/DataCopy/covid_county_population_usafacts.csv'

st.set_page_config(layout="wide")
st.header("Big Data Assignment 2", anchor=None)

MAX_COLOR_RANGE = (0,300)
MIN_COLOR_RANGE = (0,15)

df_CovidCofirmed = pd.read_csv(covid_confirmed_usafacts)
df_CovidDeaths = pd.read_csv(covid_deaths_usafacts)
df_CovidCountyPopulation = pd.read_csv(covid_county_population_usafacts)

# creating Dataframe to solve question 1
df_CovidCofirmedWeekly = df_CovidCofirmed.drop(columns = ['countyFIPS', 'County Name', 'State', 'StateFIPS'])
df_CovidCofirmedWeekly = df_CovidCofirmedWeekly.sum().to_frame()
df_CovidCofirmedWeekly.index.name = 'Date'
df_CovidCofirmedWeekly.rename(columns = {0:'Total Cases'}, inplace = True)
df_CovidCofirmedWeekly['Date'] = pd.to_datetime(df_CovidCofirmedWeekly.index)
df_CovidCofirmedWeekly["DayOfWeek"] = df_CovidCofirmedWeekly['Date'].dt.day_name()
df_CovidCofirmedWeekly['Total Cases'] = df_CovidCofirmedWeekly['Total Cases'].diff()

start = df_CovidCofirmedWeekly[df_CovidCofirmedWeekly.iloc[:,2].str.contains('Sunday')].index[0]
end = df_CovidCofirmedWeekly[df_CovidCofirmedWeekly.iloc[:,2].str.contains('Saturday')].index[-1]

df_CovidCofirmedWeekly = df_CovidCofirmedWeekly[start: end]
df_CovidCofirmedWeekly = df_CovidCofirmedWeekly.resample('W-Sun', label='left', closed = 'left', on='Date').sum().astype(int)
st.title('Weekly new cases of Covid-19 in USA', anchor=None)
chart = st.line_chart(df_CovidCofirmedWeekly)

## creating Dataframe to solve question 2

df_WeeklyCovidDeaths = df_CovidDeaths.drop(columns = ['countyFIPS', 'County Name', 'State', 'StateFIPS'])
df_WeeklyCovidDeaths = df_WeeklyCovidDeaths.sum().to_frame()

df_WeeklyCovidDeaths.index.name = 'Date'
df_WeeklyCovidDeaths.rename(columns = {0:'Total Cases'}, inplace = True)
df_WeeklyCovidDeaths['Date'] = pd.to_datetime(df_WeeklyCovidDeaths.index)
df_WeeklyCovidDeaths["DayOfWeek"] = df_WeeklyCovidDeaths['Date'].dt.day_name()
df_WeeklyCovidDeaths['Total Cases'] = df_WeeklyCovidDeaths['Total Cases'].diff()

start = df_WeeklyCovidDeaths[df_WeeklyCovidDeaths.iloc[:,2].str.contains('Sunday')].index[0]
end = df_WeeklyCovidDeaths[df_WeeklyCovidDeaths.iloc[:,2].str.contains('Saturday')].index[-1]

df_WeeklyCovidDeaths = df_WeeklyCovidDeaths[start: end]
df_WeeklyCovidDeaths = df_WeeklyCovidDeaths.resample('W-Sun', label='left', closed = 'left', on='Date').sum().astype(int)

st.title('Weekly deaths due to Covid-19 in the USA', anchor=None)
chart = st.line_chart(df_WeeklyCovidDeaths)

## creating Dataframe to solve by county
df_CovidCofirmedInCounty = df_CovidCofirmed.drop(columns = ['County Name', 'State', 'StateFIPS'])
df_CovidCofirmedInCounty = df_CovidCofirmedInCounty.groupby('countyFIPS').sum()

df_CovidCofirmedInCounty = pd.DataFrame(df_CovidCofirmedInCounty.T)
df_CovidCofirmedInCounty = df_CovidCofirmedInCounty.drop(0,1)

df_CovidCofirmedInCounty.index = pd.to_datetime(df_CovidCofirmedInCounty.index)
df_CovidCofirmedInCounty.index.name = 'Date'
df_CovidCofirmedInCounty = df_CovidCofirmedInCounty.diff().fillna(0)

start = df_CovidCofirmedInCounty[df_CovidCofirmedInCounty.index.day_name().str.contains('Sunday')].index[0]
end = df_CovidCofirmedInCounty[df_CovidCofirmedInCounty.index.day_name().str.contains('Saturday')].index[-1]
df_CovidCofirmedInCounty = df_CovidCofirmedInCounty[start: end]
df_CovidCofirmedInCounty = df_CovidCofirmedInCounty.resample('W-Sun', label='left', closed = 'left').sum()

df_CovidCofirmedInCounty = pd.DataFrame(df_CovidCofirmedInCounty.T)
df_CasesRatio = pd.merge(df_CovidCofirmedInCounty,df_CovidCountyPopulation,on='countyFIPS')
df_CasesRatio[df_CasesRatio.columns[~df_CasesRatio.columns.isin(['countyFIPS','County Name', 'State', 'population'])]] = df_CasesRatio[df_CasesRatio.columns[~df_CasesRatio.columns.isin(['countyFIPS','County Name', 'State', 'population'])]].mul(100000/df_CasesRatio['population'], axis = 0)
df_CasesRatio['countyFIPS'] = df_CasesRatio['countyFIPS'].apply(lambda x: ((str(x).zfill(5))))

st.title('Weekly new cases of Covid-19 per 100K in each county', anchor=None)
def showMap(dataframe, week, colorRange):
    fig = px.choropleth(dataframe,
                        geojson=counties,
                        locations='countyFIPS',
                        color=week,
                        color_continuous_scale="haline",
                        range_color=colorRange,
                        scope="usa",
                        labels={'Covid': 'Covid-19 Info'}
                        )
    return fig

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json', context=ssl.create_default_context(cafile=certifi.where())) as response:counties = json.load(response)

startDate = df_CasesRatio.columns[1]
endDate = df_CasesRatio.columns[-4]

from datetime import timedelta
start_time = st.slider("Select week to see result",
    min_value = startDate.to_pydatetime().date(),
    max_value = endDate.to_pydatetime().date(),
    value = df_CasesRatio.columns[1].to_pydatetime().date(),
    format = "YYYY-MM-DD",
    step = timedelta(days=7)),
st.write("Start time:", start_time[0])

newCase = st.empty()
st.title('Deaths due to Covid-19 per 100K in each county', anchor=None)
death = st.empty()
newCase.plotly_chart(showMap(df_CasesRatio,pd.to_datetime(start_time[0]), MAX_COLOR_RANGE))

## creating Dataframe to solve question 4

df_CovidDeathsInCounty = df_CovidDeaths.drop(columns = ['County Name', 'State', 'StateFIPS'])
df_CovidDeathsInCounty = df_CovidDeathsInCounty.groupby('countyFIPS').sum()

df_CovidDeathsInCounty = pd.DataFrame(df_CovidDeathsInCounty.T)
df_CovidDeathsInCounty = df_CovidDeathsInCounty.drop(0,1)

df_CovidDeathsInCounty.index = pd.to_datetime(df_CovidDeathsInCounty.index)
df_CovidDeathsInCounty.index.name = 'Date'
df_CovidDeathsInCounty = df_CovidDeathsInCounty.diff().fillna(0)

start = df_CovidDeathsInCounty[df_CovidDeathsInCounty.index.day_name().str.contains('Sunday')].index[0]
end = df_CovidDeathsInCounty[df_CovidDeathsInCounty.index.day_name().str.contains('Saturday')].index[-1]
df_CovidDeathsInCounty = df_CovidDeathsInCounty[start: end]
df_CovidDeathsInCounty = df_CovidDeathsInCounty.resample('W-Sun', label='left', closed = 'left').sum()

df_CovidDeathsInCounty = pd.DataFrame(df_CovidDeathsInCounty.T)
df_DeathRatio = pd.merge(df_CovidDeathsInCounty,df_CovidCountyPopulation,on='countyFIPS')
df_DeathRatio[df_DeathRatio.columns[~df_DeathRatio.columns.isin(['countyFIPS','County Name', 'State', 'population'])]] = df_DeathRatio[df_DeathRatio.columns[~df_DeathRatio.columns.isin(['countyFIPS','County Name', 'State', 'population'])]].mul(100000/df_DeathRatio['population'], axis = 0)

df_DeathRatio['countyFIPS'] = df_DeathRatio['countyFIPS'].apply(lambda x: ((str(x).zfill(5))))

startDate = df_DeathRatio.columns[1]
endDate = df_DeathRatio.columns[-4]
death.plotly_chart(showMap(df_DeathRatio,pd.to_datetime(start_time[0]), MIN_COLOR_RANGE))

## creating animation for question 6
if st.button('Click here to start animation'):
    for week in rrule.rrule(rrule.WEEKLY, dtstart=startDate.to_pydatetime(), until=endDate.to_pydatetime()):
        newCase.plotly_chart(showMap(df_CasesRatio, week, MAX_COLOR_RANGE))
        death.plotly_chart(showMap(df_DeathRatio,week, MIN_COLOR_RANGE))