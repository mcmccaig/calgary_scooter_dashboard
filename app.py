from time import time
from click import style
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from matplotlib.pyplot import margins
import plotly.express as px
import pandas as pd
import numpy as np
import json
import base64
import datetime as dt
from PIL import Image
from controls import VEHICLE_TYPE, UNIT_TIME, DATE_MIN, DATE_MAX, HOUR_MIN, HOUR_MAX, MONTH_MIN, MONTH_MAX, DAY_MIN, DAY_MAX, HOUR_MARKS, DAY_MARKS, MONTH_MARKS
from functions import filter_dataframe, map_list_generator, time_list_generator


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

scooter = pd.read_csv('data/trips_neigh.csv')
with open('data/Community District Boundaries.geojson', encoding='utf-8') as f:
    boundaries = json.load(f)

logo = Image.open('data/coc-logo.png')

app.layout = html.Div(
#full layout
    [
        #top row
        dbc.Row(
            [
                dbc.Col(html.Img(src=logo),
                        style={'text-align':'left'}, width={"size": 4}
                        ),
                dbc.Col(html.H2('Shared Mobility Demand Dashboard'),
                        style={'text-align':'center'}, width={"size": 4}
                        )
            ], style={'height':'auto', 'width':'auto', 'text-align': 'left', 'align-items':'center'}, className="g-0"
        ),

        #middle row
        dbc.Row(
            [
                #filters
                dbc.Col(
                    [
                        html.P(
                            'Filter by method of transport:',
                            className="control_label"
                        ),

                        dcc.RadioItems(
                            id='vehicle_selector',
                            options=[{'label': i, 'value': i.lower()} for i in VEHICLE_TYPE],
                            value='all',
                            className="dcc_control",
                        ),

                        html.P(
                            'Filter by trip date:',
                            className="control_label"
                        ),

                        dcc.DatePickerRange(
                            id='date_slider',
                            start_date = DATE_MIN,
                            end_date = DATE_MAX,
                            min_date_allowed = DATE_MIN,
                            max_date_allowed = DATE_MAX,
                            display_format='MM/DD/YYYY',
                            className="dcc_control"
                        ),

                        html.P(
                            'Filter by unit of time:',
                            className="control_label"
                        ),    

                        dcc.RadioItems(
                            id='time_unit_selector',
                            options=[{'label': i, 'value': i} for i in UNIT_TIME],
                            value='All',
                            className="dcc_control"
                        ),
                        
                        html.Div(id='hide_time_unit', children=
                            [
                            dcc.RangeSlider(step=1,
                                id='time_unit_slider',
                                allowCross=False,
                                className="dcc_control",
                                )                
                            ],
                        )   
                    ], align='inline', className="pretty_container"             
                ),   
                #info boxes
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.P('Total Number of Trips', style={'textAlign': 'center'}),
                                                html.H4(id='total_trips', style={'textAlign': 'center', "font-weight": "bold"}, className="info_text")
                                            ], style={'display': 'inline-block', 'width':'33%'},
                                            className="pretty_container"
                                        ),
                                        
                                        html.Div(
                                            [
                                                html.P('Avg Trip Distance (m)', style={'textAlign': 'center'}),
                                                html.H4(id='avg_distance', style={'textAlign': 'center', "font-weight": "bold"}, className="info_text")
                                            ], style={'display': 'inline-block', 'width':'33%'},
                                            className="pretty_container"
                                        ),

                                        html.Div(
                                            [
                                                html.P('Avg Trip Length (min)', style={'textAlign': 'center'}),
                                                html.H4(id='avg_trip', style={'textAlign': 'center', "font-weight": "bold"}, className="info_text")
                                            ], style={'display': 'inline-block', 'width':'33%'},
                                            className="pretty_container"
                                        ),
                                    ], style={'display':'flex'}
                                )
                            ]
                        ),
                    html.Div(
                        [
                           dcc.Graph(id='demand_line_plot')  
                        ], className="pretty_container"
                    )
                    ], width=8
                ),                 
            ], className='row'
        ),
        #bottom row
        dbc.Row(dcc.Graph(id='scooter_map'), 
                className="pretty_container"                
        )
    ], 
    id="mainContainer",
    style={
        "display": "flex",
        "flex-direction": "column"
    }
)


#adjust time unit slider filter
@app.callback(
    Output('time_unit_slider', 'min'),
    Output('time_unit_slider', 'max'),
    Output('time_unit_slider', 'marks'),
    Output('time_unit_slider', 'value'),
    Output('hide_time_unit', 'style'),
    Input('time_unit_selector', 'value')
)
def updateSlider(dropdown_value):
    if dropdown_value == 'All':
        return 0, 0, {0:'0'}, [0,0], {'display': 'none'}
    elif dropdown_value == 'Hour':
        return HOUR_MIN, HOUR_MAX, HOUR_MARKS, [HOUR_MIN, HOUR_MAX], {'display': 'block'}
    elif dropdown_value == 'Day':
        return DAY_MIN, DAY_MAX, DAY_MARKS, [DAY_MIN, DAY_MAX], {'display': 'block'}
    else:
        return MONTH_MIN, MONTH_MAX, MONTH_MARKS, [MONTH_MIN, MONTH_MAX], {'display': 'block'}

#update map
@app.callback(
    Output('scooter_map', 'figure'),
    Input('vehicle_selector', 'value'),
    Input('date_slider', 'start_date'),
    Input('date_slider', 'end_date'),
    Input('time_unit_selector', 'value'),
    Input('time_unit_slider', 'value')
    )

def update_map(vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider):
    df = filter_dataframe(scooter, vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider)
    community_list, trip_count_list = map_list_generator(df)
    fig = px.choropleth_mapbox(df, geojson=boundaries, featureidkey="properties.name", color_continuous_scale='reds',
                            locations=community_list, color=trip_count_list, mapbox_style="carto-positron", 
                            center={"lat":51.0447, "lon": -114.0719}, zoom=8.5) 
    fig.update_traces(text='Number of Trips')
    fig.update_layout(title = {'text':'Number of Trips by Community', 'x':0.5}, coloraxis_colorbar={'title':'Number of Trips'})
    fig.update_geos(fitbounds="locations")
    return fig

#update figure
@app.callback(
    Output('demand_line_plot', 'figure'),
    Input('vehicle_selector', 'value'),
    Input('date_slider', 'start_date'),
    Input('date_slider', 'end_date'),
    Input('time_unit_selector', 'value'),
    Input('time_unit_slider', 'value')
    )

def update_figure(vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider):
    df = filter_dataframe(scooter, vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider)
    trip_list, time_list = time_list_generator(df, time_unit_selector, time_unit_slider)
    if time_unit_selector == 'All':
        fig = px.line(df, x=time_list, y=trip_list)
        fig.update_layout(xaxis_tickformat = '%d %B (%a)<br>%Y', title = {'text':'Number of Trips by Date', 'x':0.5}, xaxis={'title':'Date'}, yaxis={'title':'Number of Trips'}, plot_bgcolor="#ededee")
        fig.update_traces(line_color="#c8102e")
    elif time_unit_selector == 'Hour':
        fig = px.line(df, x=time_list, y=trip_list)
        fig.update_layout(xaxis=dict(
            title = 'Hour',
            tickmode = 'array', 
            tickvals=time_list, 
            ticktext=[dt.time(i).strftime('%I %p') for i in time_list]
            ), title = {'text':'Number of Trips by Hour', 'x':0.5}, yaxis={'title':'Number of Trips'}, plot_bgcolor="#ededee")
        fig.update_traces(line_color="#c8102e")
    elif time_unit_selector == 'Day':
        fig = px.line(df, x=time_list, y=trip_list)
        fig.update_layout(xaxis=dict(
            title = 'Day of Week',
            tickmode = 'array', 
            tickvals=time_list, 
            ticktext=[DAY_MARKS[i] for i in time_list]
            ), title = {'text':'Number of Trips by Day of Week', 'x':0.5}, yaxis={'title':'Number of Trips'}, plot_bgcolor="#ededee")  
        fig.update_traces(line_color="#c8102e")    
    elif time_unit_selector == 'Month':
        fig = px.line(df, x=time_list, y=trip_list)
        fig.update_layout(xaxis=dict(
            title = 'Month',
            tickmode = 'array', 
            tickvals=time_list, 
            ticktext= [MONTH_MARKS[i] for i in time_list]
            ), title = {'text':'Number of Trips by Month', 'x':0.5}, yaxis={'title':'Number of Trips'}, plot_bgcolor="#ededee") 
        fig.update_traces(line_color="#c8102e")               
    return fig

#update total trips
@app.callback(Output('total_trips', 'children'),
            Input('vehicle_selector', 'value'),
            Input('date_slider', 'start_date'),
            Input('date_slider', 'end_date'),
            Input('time_unit_selector', 'value'),
            Input('time_unit_slider', 'value')
            )

def update_total_trips_text(vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider):
    df = filter_dataframe(scooter, vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider)
    return len(df.index)

#update avg trip distance
@app.callback(Output('avg_trip', 'children'),
            Input('vehicle_selector', 'value'),
            Input('date_slider', 'start_date'),
            Input('date_slider', 'end_date'),
            Input('time_unit_selector', 'value'),
            Input('time_unit_slider', 'value')
            )

def update_total_trips_text(vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider):
    df = filter_dataframe(scooter, vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider)
    time = df['trip_duration'].mean()/60
    return time.round()

#update avg trip duration
@app.callback(Output('avg_distance', 'children'),
            Input('vehicle_selector', 'value'),
            Input('date_slider', 'start_date'),
            Input('date_slider', 'end_date'),
            Input('time_unit_selector', 'value'),
            Input('time_unit_slider', 'value')
            )

def update_total_trips_text(vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider):
    df = filter_dataframe(scooter, vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider)
    return df['trip_distance'].mean().round()


if __name__ == '__main__':
    app.run_server(debug=True)