# Script for scrapping dynamic bike data from JCDecaux API
import database.send_email as send_email
import database.login as login
import pymysql
import requests
import time
from datetime import datetime

while True:
    try:
        # Connect to database
        conn = pymysql.connect(host=login.dbHost, user=login.dbUser, password=login.dbPassword, database=login.dbDatabase)
        cursor = conn.cursor()
        print("Connection to database successful!")

        # Connect to JCDecaux API
        r = requests.get(login.jcdUri, params={'contract':login.jcdName,
                                        'apiKey': login.jcdKey})

        if r.status_code == 200:
            # If connection successful:
            print('Connection to JCDecaux successful!')
            data = r.json()

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%d-%m-%Y")
            # For each station, extract the following data points:
            for station in data:
                number = station.get('number')
                name = station.get('name')
                station_capacity = station.get('bike_stands')
                available_bike_stands = station.get('available_bike_stands')
                available_bikes = station.get('available_bikes')
                status = station.get('status')
                last_update = station.get('lastUpdate')

                # Try insert this data into the static table.
                try:
                    sql_dynamic = 'INSERT INTO dynamic(number, name, bike_stands, available_bike_stands, available_bikes, status, last_update,current_date,current_time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);'
                    dynamic_values = (number, name, station_capacity, available_bike_stands, available_bikes, status, last_update,current_date,current_time)
                    cursor.execute(sql_dynamic, dynamic_values)
                    conn.commit()

                except Exception as e:
                    print(f"Database error: {e}")
                    # Rollback any changes made to database if there was an error
                    #and send an email to log the error
                    conn.rollback() 
                    send_email.email_error(e)
                    break
            
            # Confirm rows added successfully & log
            
            print(f"Rows inserted successfully on {current_date} at {current_time}")
        
        else:
            print("Error: API request failed with status code", r.status_code)
            send_email.email_error(r.status_code)

        # Close the connection
        cursor.close()
        conn.close()
    except pymysql.Error as e:
        print("Error connecting to database:", e)
        send_email.email_error(e)

    # Add 5 minute repeat.
    time.sleep(300)

