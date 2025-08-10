import pandas as pd
import numpy as np
import geopandas as gpd
import dash
from dash import Dash, html, dcc, dash_table, Input, Output, callback_context
import plotly.express as px

from world_health_data import WorldHealthData

app = Dash()
db = WorldHealthData()
data = db.get_all_data()

global CURRENT_DATE_RANGE, CURRENT_INDICATOR, CURRENT_COUNTRY
CURRENT_INDICATOR = "Life Expectancy"
CURRENT_COUNTRY = "United States"
CURRENT_DATE_RANGE = [2000, 2020]

def render_page_filters():
    """ Renders the filters for the dashboard """
    dates = data.index.get_level_values("Date").unique().to_list()
    indicators = data.columns.to_list()

    return html.Div([
        html.Div([
            html.Label("Indicator"),
            dcc.Dropdown(indicators, CURRENT_INDICATOR, id="indicator-dropdown", multi=False)
        ], style={"padding": "10px", "flex": 1}),
        html.Div([
            html.Label("Dates"),
            dcc.RangeSlider(np.min(dates), np.max(dates), 1, value=[np.min(dates), np.max(dates)], marks=None, tooltip={
                "placement": "bottom",
                "always_visible": True,
                "style": {"fontSize": "20px"}
            }, id="date-range-slider")
        ], style={"padding": "10px", "flex": 1})
    ], style={"display": "flex", "flexDirection": "row"})

def render_country_filter():
    """ Renders the country filter """

    countries = data.index.get_level_values("Country").unique().to_list()

    return html.Div([
        html.Label("Country"),
        dcc.Dropdown(countries, CURRENT_COUNTRY, id="country-dropdown", multi=False)
        ], style={"padding": "10px"})
    
def render_choropleth_map(data, indicator):
    """ Renders the choropleth map using the given data """

    indicator_data = data[indicator].reset_index().drop(columns="Date")
    indicator_data = indicator_data.groupby(["Country", "CountryId"]).mean().reset_index()

    return px.choropleth(indicator_data, locations="CountryId", 
                         color=indicator, hover_name="Country", 
                         color_continuous_scale=px.colors.sequential.Peach)

def render_time_series(data, country, indicator):
    """ Renders the time series chart for the given indicator """

    indicator_data = data[indicator].reset_index()
    indicator_data = indicator_data[indicator_data["Country"] == country]

    return px.line(indicator_data, x="Date", y=indicator, title=f"{indicator} in {country}")

def construct_summary_table(indicator_data, indicator):
    """ Construct the data into a summary table """
    df = indicator_data.pivot(columns="Country", index="Date", values=indicator)
    df_summary = df.describe().transpose().apply(lambda x: np.round(x, decimals=2))
    return df_summary[["min", "max", "mean", "std"]].rename(columns={"min": "Minimum", "max": "Maximum", "mean": "Average", "std": "Standard Deviation"}).reset_index()
    # return df_summary.transpose()

def render_summary_table(data, indicator):
    """ Renders the summary table for the given country """
    
    indicator_data = data[indicator].reset_index()
    table_data = construct_summary_table(indicator_data=indicator_data, indicator=indicator)

    return html.Div([
        html.H4(f"{indicator} Summary Data"),
        dash_table.DataTable(id='summary-table',
                             columns=[{"name": i, "id": i} for i in table_data.columns],
                             data=table_data.to_dict('records'),
                             style_table={'overflowY': 'auto'},
                             fixed_rows={'headers': True},
                             sort_action="native",
                             sort_mode="multi",
                             style_data={'height': 'auto', 'whiteSpace': 'normal'},
                             style_cell={'maxWidth': '250px', 'minWidth': '100px'})
    ], id="summary-table-wrapper", style={"flex": 1})

app.layout = html.Div([
    html.H1("Health Indicators Dashboard", style={"textAlign": "center"}),
    render_page_filters(),
    html.Div([
        dcc.Graph(figure=render_choropleth_map(data, CURRENT_INDICATOR), id="choropleth-map")
    ], style={"justifyContent": "center"}),
    html.Div([
        html.Div([
            render_summary_table(data, CURRENT_INDICATOR)
        ], style={"flex": 1}),
        html.Div([
            render_country_filter(),
            dcc.Graph(figure=render_time_series(data, CURRENT_COUNTRY, CURRENT_INDICATOR), id="time-series")
        ], style={"flex": 2, "height": "600px"})
    ], style={"display": "flex", "gap": "10px"})
], style={"padding": "1rem"})

@app.callback(
    Output('choropleth-map', 'figure'),
    Output('summary-table-wrapper', 'children'),
    Output('time-series', 'figure'),
    Input('indicator-dropdown', 'value'),
    Input('date-range-slider', 'value'),
    Input('country-dropdown', 'value')
)
def update_figures(indicator, date_range, country):
    triggered_id = callback_context.triggered_id

    # Default to global values if None
    global CURRENT_COUNTRY, CURRENT_DATE_RANGE, CURRENT_INDICATOR
    if date_range is None:
        date_range = CURRENT_DATE_RANGE
    if indicator is None:
        indicator = CURRENT_INDICATOR
    if country is None:
        country = CURRENT_COUNTRY

    # Filter data only once
    filtered_data = data.query(f'Date >= {date_range[0]} and Date <= {date_range[1]}')
    print(filtered_data.head())
    # filtered_data = data[(data.Date >= date_range[0]) & (data.Date <= date_range[1])]

    # Save current selections (if needed globally)
    CURRENT_DATE_RANGE = date_range
    CURRENT_INDICATOR = indicator
    CURRENT_COUNTRY = country

    # Always update the time series
    time_series = render_time_series(data=filtered_data, country=country, indicator=indicator)

    # If the trigger was country change, skip recomputing the other charts
    if triggered_id == 'country-dropdown':
        return dash.no_update, dash.no_update, time_series

    # Otherwise update all
    choropleth_map = render_choropleth_map(data=filtered_data, indicator=indicator)
    summary_table = render_summary_table(data=filtered_data, indicator=indicator)

    return choropleth_map, summary_table, time_series


if __name__ == '__main__':
    app.run(debug=True)
