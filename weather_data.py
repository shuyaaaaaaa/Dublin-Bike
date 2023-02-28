# Script for scrapping dynamic weather data from openWeatherMap API
import login
import pymysql
import requests
import time
import send_email
from datetime import datetime

while True:
    try:
        # Connect to database
        conn = pymysql.connect(host=login.dbHost, user=login.dbUser, password=login.dbPassword, database=login.dbDatabase)
        cursor = conn.cursor()
        print("Connection to database successful!")

        # Connect to OpenWeather API
        r = requests.get(login.owUri, params={'lat': login.owLat, 'lon': login.owLon, 'appid': login.owKey})

        if r.status_code == 200:
            # If connection successful:
            print('Connection to OpenWeather Map successful!')
            data = r.json()

            # Extract the information for the current weather

            latitude=data.get('coord').get('lat')
            longitude=data.get('coord').get('lon')
            weather_id=data.get('weather')[0].get('id')
            weather_main=data.get('weather')[0].get('main')
            weather_description=data.get('weather')[0].get('description')
            weather_icon=data.get('weather')[0].get('icon')

            temperature=data.get('main').get('temp')
            feels_like=data.get('main').get('feels_like')
            temp_min=data.get('main').get('temp_min')
            temp_max=data.get('main').get('temp_max')
            pressure=data.get('main').get('pressure')
            humidity=data.get('main').get('humidity')

            visibility=data.get('visibility')
            wind_speed=data.get('wind').get('speed')
            wind_direction=data.get('wind').get('deg')
            
            #multiple values available here
            #how to handle if one is missing?
            if data.get('rain') is None:
                rain_1=0
                rain_3=0#zero means no values recorded
            else:
                rain_1=data.get('rain').get('1h')
                rain_3=data.get('rain').get('3h')

            if data.get('snow') is None:
                snow_1=0
                snow_3=0#zero means no values recorded
            else:
                snow_1=data.get('rain').get('1h')
                snow_3=data.get('rain').get('3h')
    
            if data.get('clouds') is None:
                clouds=0
            else:
                clouds=data.get('clouds').get('all')

            sunrise=data.get('sys').get('sunrise')
            sunset=data.get('sys').get('sunset')

            time_w=data.get('dt')

            # Try insert this data into the weather table.
            try:
                sql_weather = 'INSERT INTO weather(latitude,longitude,weather_id,weather_main ,weather_description,weather_icon,temperature,feels_like,temp_min,temp_max,pressure,humidity,visibility,wind_speed,wind_direction,rain_1,rain_3,snow_1,snow_3,clouds,sunrise,sunset,time_w) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
                weather_values = (latitude,longitude,weather_id,weather_main ,weather_description,weather_icon,temperature,feels_like,temp_min,temp_max,pressure,humidity,visibility,wind_speed,wind_direction,rain_1,rain_3,snow_1,snow_3,clouds,sunrise,sunset,time_w)
                cursor.execute(sql_weather, weather_values)
                conn.commit()

            except Exception as e:
                print(f"Database error: {e}")
                send_email.email_error(e)
                # Rollback any changes made to database if there was an error
                conn.rollback() 
                break

            # Confirm rows added successfully
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%d-%m-%Y")
            print(f"Rows inserted successfully on {current_date} at {current_time}")

            # Close the connection
            cursor.close()
            conn.close()        
        else:
            print("Error: API request failed with status code", r.status_code)
            send_email.email_error(r.status_code)

    except pymysql.Error as e:
        print("Error connecting to database:", e)
        send_email.email_error(e)

    # Add 5 minute repeat.
    time.sleep(300)

