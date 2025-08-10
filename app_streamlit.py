import streamlit as st
import pandas as pd
import numpy as np
from world_health_data import WorldHealthData

st.title("World Health Indicators Dashboard")

def load_data():
    """ Load the data from the CSV file """
    db = WorldHealthData()
    return db.get_all_data()

# TODO: Shape the data into the correct summary table
data_load_state = st.text("Loading data...")
data = load_data()
data_load_state.text("Done! Data has been loaded.")

st.subheader("Raw Data")
st.write(data)

# TODO: Will need to add Latitude and Longitude data to make this work
# st.subheader("Choropleth Map")
# st.map(data)

# Line Plot
# TODO: Filter by country
# TODO: Apply the selected indicator
st.subheader("Time Series")
australia_data = data.reset_index()
australia_data = australia_data[australia_data["Country"] == "Australia"]
st.line_chart(data=australia_data, x="Date", y="Life Expectancy")