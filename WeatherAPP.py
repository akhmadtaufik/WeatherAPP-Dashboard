import json
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# Read PWD
f = open("config.txt", "r")
lines = f.readlines()
myPass = lines[0].strip()
myAPI  = lines[1]
f.close()

# Getting API Data
url_current = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
url_historical = 'http://api.openweathermap.org/data/2.5/onecall/timemachine?lat={}&lon={}&dt={}&appid={}'

# Getting LATEST WEATHER DATA
def getWeather(city):
    result = requests.get(url_current.format(city, myAPI))
    if result:
        raw_data = result.json()
        #st.write(raw_data)
        country = raw_data['sys']['country']
        temp = raw_data['main']['temp'] - 273.15
        temp_feels = raw_data['main']['feels_like'] - 273.15
        humidity = raw_data['main']['humidity'] - 273.15
        icon = raw_data['weather'][0]['icon']
        long = raw_data['coord']['lon']
        lat = raw_data['coord']['lat']
        desc = raw_data['weather'][0]['description']
        data = [country, round(temp,1), round(temp_feels,1), humidity, 
                lat, long, icon, desc]
        return data, raw_data
    else:
        print("Data Not Found!!")
        
# Getting Historical Data
def getHistData(lat, long, start):
    resp = requests.get(url_historical.format(lat, long, start, myAPI))
    hist = resp.json()
    temp = []
    for hour in hist['hourly']:
        t = hour['temp']
        temp.append(t)
    return hist, temp

# Streamlit

st.title("Streamlit Weather APP from OpenWeather API")

col1, col2 = st.columns(2)
with col1:
    city_name = st.text_input('Please Enter City Name')
with col2:
    if city_name:
        data, raw_data = getWeather(city_name)
        #st.write(data)
        st.success('Current: ' + str(round(data[1], 2)))
        st.info('Feels Like: ' + str(round(data[2], 2)))
        st.info('Humidity: ' + str(round(data[3], 2)))
        st.subheader('Status ' + data[7])
        web_str = "![Alt Text]"+"(http://openweathermap.org/img/wn/"+str(data[6])+"@2x.png)"
        st.markdown(web_str)
        
if city_name:
    showHist = st.expander(label='Last 5 Days History')
    with showHist:
        startDateString = st.date_input('Current Date')
        dateDf = []
        maxTempDf = []
        for i in range(5):
            dateStr = startDateString - timedelta(i)
            startDate = datetime.strptime(str(dateStr), "%Y-%m-%d")
            timeStamp1 = datetime.timestamp(startDate)
            hist, temp = getHistData(data[4], data[5], int(timeStamp1))
            dateDf.append(dateStr)
            maxTempDf.append(max(temp) - 273.5)
            
        df = pd.DataFrame()
        df['Date'] = dateDf
        df['Max Temperature'] = maxTempDf
        st.table(df)

    st.map(pd.DataFrame({'lat' : [data[4]], 'lon' : [data[5]]}, columns=['lat', 'lon']))