
import pymysql

host='comp30830.cfgxtnlmswbs.eu-west-1.rds.amazonaws.com'
user='admin'
password='softwarebikes1'
database='dublinbikes'

conn = pymysql.connect(host=host, user=user, password=password, database=database)

cursor = conn.cursor()

#static-once this table is created and filled once it will only need to be updated less often
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
    print (res)
except Exception as e:
    print(e)


##dynamic table=what will change over time-this will be updated every 5 minutes
sql="""
CREATE TABLE IF NOT EXISTS dynamic ( 
bike_stands INTEGER,
available_bike_stands INTEGER,
available_bikes INTEGER,
status VARCHAR(256),
last_update INTEGER
)
"""
try:
    res=cursor.execute(sql)
    print (res)
except Exception as e:
    print(e) #, traceback.format_exc())


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
    print (res)
except Exception as e:
    print(e) #, traceback.format_exc())



cursor.close()
cursor.close()