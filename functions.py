import pandas as pd
import numpy as np
import datetime as dt
import json
import plotly.express as px

scooter = pd.read_csv('data/trips_neigh.csv')
with open('data/Community District Boundaries.geojson', encoding='utf-8') as f:
    boundaries = json.load(f)

def filter_dataframe(df, vehicle_select, start_date, end_date, time_unit_selector, time_unit_slider):
    #vehicle filters
    if vehicle_select != 'all':
        df = df[df['vehicle_type'] == vehicle_select]
    #date slider filters
    df = df[(df['dt_start_date'] >= start_date)
             & (df['dt_start_date'] <= end_date)]
    #if unit of time is filtered
    if time_unit_selector != 'All':   
        if time_unit_selector == 'Hour':
            df = df[(df['start_hour'] >= time_unit_slider[0]) 
                    & (df['start_hour'] <= time_unit_slider[1])]
        elif time_unit_selector == 'Day':
            df = df[(df['dt_dayofweek'] >= time_unit_slider[0]) 
                    & (df['dt_dayofweek'] <= time_unit_slider[1])]        
        elif time_unit_selector == 'Month':
            df = df[(df['dt_month'] >= time_unit_slider[0]) 
                    & (df['dt_month'] <= time_unit_slider[1])]   
    return df

def map_list_generator(df):
    df = df.groupby(['name']).size()
    df = pd.DataFrame(df)
    df = df.reset_index()
    df = df.rename(columns={'name':'name', 0:'count'})
    
    community_names = []
    for i in boundaries['features']:
        community_names.append(i['properties']['name'])
    community_names = sorted(community_names)

    missing_list = []
    for i in community_names:
        if i not in df['name'].tolist():
            missing_list.append(i)
    missing_list = pd.DataFrame(missing_list, columns=['name'])
    missing_list['count'] = 0

    df = df.append(missing_list)
    df = df.sort_values(by=['name'])

    community_list = df['name'].tolist()
    trip_count_list =  df['count'].tolist()
    
    return community_list, trip_count_list

def time_list_generator(df, time_unit_selector, time_unit_slider):
    if time_unit_selector == 'All':
        trip_list = df.groupby(['start_date']).size().tolist()
        time_list = sorted(df['start_date'].unique().tolist())
        time_list = [dt.datetime.strptime(date, '%Y/%m/%d').date() for date in time_list]
    elif time_unit_selector == 'Hour':
        trip_list = df.groupby(['start_hour']).size().tolist()
        time_list = list(range(24))
        trip_list = trip_list[:time_unit_slider[1]+1]
        time_list = time_list[time_unit_slider[0]:time_unit_slider[1]+1]
    elif time_unit_selector == 'Day':
        trip_list = df.groupby(['dt_dayofweek']).size().tolist()
        time_list = list(range(7))
        trip_list = trip_list[:time_unit_slider[1]+1]
        time_list = time_list[time_unit_slider[0]:time_unit_slider[1]+1]
    elif time_unit_selector == 'Month':
        trip_list = df.groupby(['dt_month']).size().tolist()
        time_list = [7,8,9]
        trip_list = trip_list[:time_unit_slider[1]-7+1]
        time_list = time_list[time_unit_slider[0]-7:time_unit_slider[1]-7+1]        
    return trip_list, time_list