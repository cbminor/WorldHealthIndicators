# Global Health Indicator Explorer

## Project Overview
Create an interactive web application that allows users to explore global health trends across countries and time. The app will visualize 5 key health indicators from the World Bank dataset to help users gain insight into patterns in health investment and outcomes.

Three separate web applications will be created to compare the dashboard creation tools.

## Goals

* Enable users to interactively explore global health indicators by country, year, and indicator
* Provide visual context through a choropleth map and time series plots
* Present key summary statistics for each indicator and selected year

## Indicators to Explore

* Life Expectancy
* Health Expenditure per Capita
* Under-5 Mortality Rate
* Immunization (Measles, % of children)
* Physicians per 1,000 People

## Core Features
* Dropdown to Select Indicator
    * Display name (e.g., "Life Expectancy")
    * Pulls corresponding data
* Year Selector (Slider)
    * Limit to years where data is available for all indicators (e.g., 2000–2020)
* Choropleth Map
    * Color-coded by indicator value per country
    * Hover for value and country name
    * Click to select country for time series plot
* Time Series Plot
    * Line graph showing the selected indicator over time for the selected country
* Summary Stats
    * Min, max, mean value of the indicator for the selected year

## Deliverables

* Fully functional app in all 3 frameworks (Dash, Streamlit, Shiny)
* Clean and reusable dataset
