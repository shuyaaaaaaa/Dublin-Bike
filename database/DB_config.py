import database.login as login
import pymysql

#creating connection using pymysql
conn = pymysql.connect(host=login.dbHost, user=login.dbUser, password=login.dbPassword, database=login.dbDatabase)
cursor = conn.cursor()

#static table creation
#This table will not change over time
sql ='''
CREATE TABLE IF NOT EXISTS static ( 
number INTEGER,
contract_name VARCHAR(256),
name VARCHAR(256),
address VARCHAR(256),
position_lat REAL,
position_lng REAL,
banking BOOLEAN,
bonus BOOLEAN
)
'''
try:
    res=cursor.execute("DROP TABLE IF EXISTS station")
    res=cursor.execute(sql)
    #result will be zero if table is created
    print (res)
except Exception as e:
    print(e)

#dynamic table creation
#what will change over time-this will be updated every 5 minutes to collect data
sql="""
CREATE TABLE IF NOT EXISTS dynamic ( 
number INTEGER,
name VARCHAR(256),
bike_stands INTEGER,
available_bike_stands INTEGER,
available_bikes INTEGER,
status VARCHAR(256),
last_update INTEGER
)
"""
try:
    res=cursor.execute(sql)
    #result will be zero if table is created
    print (res)
except Exception as e:
    print(e)

#creating weather data table
sql="""
CREATE TABLE IF NOT EXISTS weather ( 
latitude REAL,
longitude REAL,
weather_id INTEGER,
weather_main VARCHAR(256),
weather_description VARCHAR(256),
weather_icon VARCHAR(256),
temperature REAL,
feels_like REAL,
temp_min REAL,
temp_max REAL,
pressure REAL,
humidity REAL,
visibility REAL,
wind_speed REAL,
wind_direction REAL,
rain_1 REAL,
rain_3 REAL,
snow_1 REAL,
snow_3 REAL,
clouds REAL,
sunrise INTEGER,
sunset INTEGER,
time_w INTEGER
)
"""
try:
    res=cursor.execute(sql)
    #print 0 if table is created
    print (res)
except Exception as e:
    print(e)

cursor.close()
conn.close()