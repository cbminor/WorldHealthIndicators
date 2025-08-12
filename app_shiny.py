import seaborn as sns
import numpy as np
import pandas as pd
from world_health_data import WorldHealthData
from shiny import App, reactive, render, ui
import shiny.express as sx
import plotly.express as px

# Constants
INDICATORS = ["Life Expectancy", "Health Expenditure", "Mortality Rate", "Polio Immunization", "Physician Count"]

# Load data once
db = WorldHealthData()
data = db.get_all_data()
data.reset_index(inplace=True)

# App UI
app_ui = ui.page_fluid(
    ui.layout_columns(
    ui.input_select("indicator", label="Select an Indicator", choices=INDICATORS, selected="Life Expectancy"),
    ui.input_slider("years", label="Years", max=int(np.max(data.Date)), min=int(np.min(data.Date)), value=[2000, 2020], sep="")
    ),
    ui.output_ui("choropleth_card"),
    ui.layout_columns(
        ui.card(
            ui.output_ui("summary_card"),
            full_screen=True
        ),
        ui.card(
            ui.card_header("Select a Country"),
            ui.input_select("country", label="", choices=sorted(data.Country.unique().tolist())),
            full_screen=True,
        ),
        ui.card(
            ui.output_ui("timeseries_card"),
            full_screen=True,
        ),
    )
)

# Server logic
def server(input, output, session):

    @reactive.Calc
    def filtered_data():
        # Filter data by year range from slider
        years = input.years()
        df = data[(data.Date >= years[0]) & (data.Date <= years[1])]
        return df

    @output
    @render.ui
    def choropleth_card():
        # Reactive card with header and plot
        return ui.card(
            ui.output_ui("choropleth_header"),
            ui.output_plot("choropleth_map"),
            full_screen=True,
        )

    @output
    @render.ui
    def choropleth_header():
        # Header depends on indicator
        return ui.card_header(f"{input.indicator()} Choropleth Map")

    @output
    @render.plot
    def choropleth_map():
        # TODO: This isn't working. Fix. 
        df = filtered_data()
        fig = px.choropleth(
            df,
            locations="CountryId",
            color=input.indicator(),
            color_continuous_scale="Viridis",
            title=f"{input.indicator()} Choropleth"
        )
        return 
        return fig
    

    @render.data_frame
    def summary_grid():
        # Card with header and data grid
        return render.DataGrid(filtered_data())
    
    @output
    @render.ui
    def summary_card():
        return ui.TagList(
            ui.card_header(f"{input.indicator()} Summary Table"),
            ui.output_data_frame("summary_grid")
        )

    @output
    @render.ui
    def timeseries_card():
        # Card with header and plot for time series
        return ui.TagList(
            ui.card_header(f"{input.indicator()} Time Series for {input.country()}"),
            ui.output_plot("time_series_plot")
        )

    @output
    @render.plot
    def time_series_plot():
        df = filtered_data()
        country_data = df[df.Country == input.country()]
        sns.set_theme(style="whitegrid")
        fig = sns.lineplot(data=country_data, x="Date", y=input.indicator()).get_figure()
        return fig

app = App(app_ui, server)
