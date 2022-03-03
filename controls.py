import pandas as pd
scooter = pd.read_csv('data/pilot_trips_dt.csv')
scooter['dt_start_date'] = pd.to_datetime(scooter['dt_start_date'])

VEHICLE_TYPE = ['All', 'Bicycle', 'Scooter']

UNIT_TIME = ['All', 'Hour', 'Day', 'Month']

DATE_MIN = pd.to_datetime(scooter['start_date']).dt.date.min()
DATE_MAX = pd.to_datetime(scooter['start_date']).dt.date.max()

HOUR_MIN = scooter['start_hour'].min()
HOUR_MAX = scooter['start_hour'].max()

MONTH_MIN = scooter['dt_start_date'].dt.month.min()
MONTH_MAX = scooter['dt_start_date'].dt.month.max()

DAY_MIN = scooter['dt_dayofweek'].min()
DAY_MAX = scooter['dt_dayofweek'].max()

HOUR_MARKS = {int(i): str(i) for i in range(24)}
DAY_MARKS = {0: 'Sunday', 1: 'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday'}
MONTH_MARKS = {7: 'July', 8:'August', 9:'September'}
