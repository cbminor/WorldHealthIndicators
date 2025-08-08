import pandas as pd
import numpy as np
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.express as px

from world_health_data import WorldHealthData

app = Dash()
db = WorldHealthData()
data = db.get_all_data()

def render_page_filters():
    """ Renders the filters for the dashboard """
    dates = data.date.unique().tolist()
    indicators = data.columns.to_list()

    return html.Div([
        html.Div([
            html.Label("Indicator"),
            dcc.Dropdown(indicators, "Life Expectancy", id="indicator-dropdown", multi=False)
        ], style={"padding": "10px", "flex": 1}),
        html.Div([
            html.Label("Country"),
            dcc.RangeSlider(dates, value=[np.min(dates), np.max(dates)], id="date-range-slider")
        ], style={"padding": "10px", "flex": 1})
    ], style={"display": "flex", "flexDirection": "row"})

def render_country_filter():
    """ Renders the country filter """

    countries = data.index.get_level_values("Country").unique().to_list()

    return html.Div([
        html.Label("Country"),
        dcc.Dropdown(countries, "United States", id="country-dropdown", multi=False)
        ], style={"padding": "10px"}),
    
def render_choropleth_map(data, indicator):
    """ Renders the choropleth map using the given data """

    indicator_data = data[indicator].reset_index()

    return px.choropleth(indicator_data, locations="iso_alpha", 
                         color=indicator, hover_name="Country", 
                         color_continuous_scale=px.colors.sequential.Peach)

def render_time_series(data, country, indicator):
    """ Renders the time series chart for the given indicator """

    indicator_data = data[indicator].reset_index()
    indicator_data = indicator_data[indicator_data["Country"] == country]

    return px.line(indicator_data, x="Date", y=indicator, title=f"{indicator} in {country}")

def construct_summary_table(indicator_data):
    """ Construct the data into a summary table """
    df = indicator_data.pivot(columns="Country", index="Date")
    return df.describe().transpose()

def render_summary_table(data, country, indicator):
    """ Renders the summary table for the given country """
    
    indicator_data = data[indicator].reset_index()
    table_data = construct_summary_table(indicator_data=indicator_data)

    return html.Div([
        html.H4(f"{indicator} Summary Data"),
        dash_table.DataTable(id='summary-table',
                             columns=[{"name": i, "id": i} for i in table_data.columns],
                             data=table_data.to_dict('records'),
                             style_table={'overflowY': 'auto'},
                             fixed_rows={'headers': True},
                             sort_action="native",
                             sort_mode="multi")
    ], id="summary-table-wrapper")
