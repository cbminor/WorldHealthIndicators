import seaborn as sns
import numpy as np
from world_health_data import WorldHealthData
from shiny import reactive
import shiny.express as sx
from shiny.express import input, ui, render
import plotly.express as px
from shinywidgets import render_plotly

# Constants
INDICATORS = ["Life Expectancy", "Health Expenditure", "Mortality Rate", "Polio Immunization", "Physician Count"]

# Load data once
db = WorldHealthData()
data = db.get_all_data()
data.reset_index(inplace=True)

# --- UI ---
sx.ui.page_opts(full_width=False)

sx.ui.h1("World Health Indicators Dashboard", style="margin-top: 1rem; text-align: center;")


with ui.layout_columns(fill=False, style="text-align: center;"):
    ui.input_select("indicator", label="Select an Indicator", choices=INDICATORS, selected="Life Expectancy")
    ui.input_slider("years", label="Years", max=int(np.max(data.Date)), min=int(np.min(data.Date)), value=[2000, 2020], sep="")

with ui.card(full_screen=True, height="500px"):
    ui.card_header("Choropleth Map")
    
    @render_plotly
    def choropleth_map():
        indicator = input.indicator()
        filt_data = filtered_df()[["CountryId", indicator]].groupby("CountryId").mean().reset_index()
        fig = px.choropleth(
            filt_data,
            locations="CountryId",
            color=input.indicator(),
            color_continuous_scale="Viridis",
        )
        return fig

with ui.layout_columns(fill=True):
    with ui.card(full_screen=True):
        ui.card_header("Data Summary")

        @render.data_frame
        def summary_table():
            indicator = input.indicator()
            table_data = filtered_df()[["Country", "Date", indicator]]
            table_data = table_data.pivot(columns="Country", index="Date", values=indicator)
            data_summary = table_data.describe().transpose().apply(lambda x: np.round(x, decimals=2))
            data_summary = data_summary[["min", "max", "mean", "std"]].rename(columns={"min": "Minimum", 
                                                                                       "max": "Maximum", 
                                                                                       "mean": "Average", 
                                                                                       "std": "Standard Deviation"}).reset_index()
            return render.DataGrid(data_summary)
        
    with ui.card(full_screen=True):
        ui.card_header("Time Series")
        ui.input_select("country", label="Select a Country", choices=data.Country.unique().tolist())

        @render.plot
        def time_series():
            time_series_data = filtered_df()
            time_series_data = time_series_data[time_series_data[input.indicator()].notna()]
            time_series_data = time_series_data[time_series_data["Country"] == input.country()]
            return sns.lineplot(data=time_series_data, x="Date", y=input.indicator())

# --- Server Logic ---
@reactive.calc
def filtered_df():
    return data[(data.Date >= input.years()[0]) & (data.Date <= input.years()[1])]
