import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

Data_url = 'Motor_Vehicle_Collisions_-_Crashes.csv'

st.title('Motor Vehicle Collision in New York City')
st.markdown('This application is  a streamlit dashboard that can be used'
'to analyze motor vehicle collions in NYC')

@st.cache(persist=True)
def load_data(nrow):
    data = pd.read_csv(Data_url, nrows = nrow, parse_dates = [['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns = {'crash_date_crash_time': 'crash/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

st.header('Where are the most people injured in NYC?')
injured_people = st.slider('Number of persons injured in crash', 0, 19)
st.map(data.query('injured_persons >= @injured_people')[['latitude','longitude']].dropna(how="any"))

st.header('How many collisions occur in a given time of day?')
hour = st.slider('Hour to look at', 0,23)
data = data[data['crash/time'].dt.hour == hour]

st.markdown('Vehicle collisions between %i:00 and %i:00' % (hour, hour+1))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        'latitude': midpoint[0],
        'longitude': midpoint[1],
        'zoom':11,
        'pitch': 50,
    },
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data = data[['crash/time','latitude','longitude']],
            get_position = ['longitude','latitude'],
            radius = 100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range = [0,1000],
        ),
    ],
))

st.subheader('Breakdown by minute between %i:00 and %i:00' % (hour, (hour+1) %24))
filtered = data[
    (data['crash/time'].dt.hour >= hour) & (data['crash/time'].dt.hour < (hour+1))
]

hist = np.histogram(filtered['crash/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header('Top 5 dangerous streets by affected type')
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query('injured_pedestrians >= 1')[['on_street_name','injured_pedestrians']].sort_values(by=['injured_pedestrians'], ascending = False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(original_data.query('injured_cyclists >= 1')[['on_street_name','injured_cyclists']].sort_values(by=['injured_cyclists'], ascending = False).dropna(how='any')[:5])

else:
    st.write(original_data.query('injured_motorists >= 1')[['on_street_name','injured_motorists']].sort_values(by=['injured_motorists'], ascending = False).dropna(how='any')[:5])


if st.checkbox('Show Raw Data', False):
    st.subheader('Raw Data')
    st.write(data)