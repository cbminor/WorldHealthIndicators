import json
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from world_health_data import WorldHealthData

INDICATORS = ["Life Expectancy", "Health Expenditure", "Mortality Rate", "Polio Immunization", "Physician Count"]

st.set_page_config(layout="wide")

st.title("World Health Indicators Dashboard")

def load_data():
    """ Load the data from the CSV file """
    db = WorldHealthData()
    return db.get_all_data()

def color_scale(indicator_value, min_val, max_val):
    """ Returns a color between red and blue based on the indicator value """
    if indicator_value is None:
        return [200, 200, 200]
    norm = (indicator_value - min_val) / (max_val - min_val)
    norm = max(0, min(1, norm))
    r = int(norm * 255)
    g = 0
    b = int((1 - norm) * 255)
    return [r,g,b]

data = load_data()
data.reset_index(inplace=True)

# Filters
dates = data.Date.unique().tolist()
selected_indicator = st.selectbox('Select Indicator', options=INDICATORS)
year_range = st.slider("Select the range of years", np.min(dates), np.max(dates), (2000, 2020))

# Filter the Data
filtered_data = data[(data.Date >= year_range[0]) & (data.Date <= year_range[1])]

# Create Choropleth Map
with open("data/countries.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)
for feature in geojson_data["features"]:
    country_code = feature["properties"]["ISO3166-1-Alpha-3"]
    match = filtered_data.loc[data["CountryId"] == country_code]
    if not match.empty:
        feature["properties"]["value"] = float(match[selected_indicator].mean())
    else:
        feature["properties"]["value"] = None
min_indicator = np.min(filtered_data[selected_indicator]) 
max_indicator = np.max(filtered_data[selected_indicator])
for feature in geojson_data["features"]:
    feature["properties"]["color"] = color_scale(indicator_value=feature["properties"]["value"], min_val=min_indicator, max_val=max_indicator)
layer = pdk.Layer("GeoJsonLayer", geojson_data, stroked=True, filled=True, get_fill_color="properties.color", get_line_color=[0, 0, 0], pickable=True)
view_state = pdk.ViewState(latitude=20,longitude=0,zoom=1)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, map_style="mapbox://styles/mapbox/light-v9", tooltip={"text": "{name}\n" + selected_indicator.title() + ": {value}"})) # ignore: type

# Create the columns
col1, col2 = st.columns(2)

# Create the summary table
table_data = filtered_data[["Country", "Date", selected_indicator]]
table_data = table_data.pivot(columns="Country", index="Date", values=selected_indicator)
data_summary = table_data.describe().transpose().apply(lambda x: np.round(x, decimals=2))
data_summary = data_summary[["min", "max", "mean", "std"]].rename(columns={"min": "Minimum", "max": "Maximum", "mean": "Average", "std": "Standard Deviation"}).reset_index()
col1.subheader("Summary Table")
col1.write(data_summary)

# Line Plot
col2.subheader(f"Time Series Data By Country")
selected_country = col2.selectbox("Select Country", data.Country.unique().tolist()) 
filtered_data = filtered_data[filtered_data.Country == selected_country]
time_series_data = filtered_data.reset_index()
time_series_data = time_series_data[time_series_data["Country"] == selected_country]
col2.line_chart(data=time_series_data, x="Date", y=selected_indicator)
