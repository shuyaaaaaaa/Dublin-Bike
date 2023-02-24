# Script for scrapping dynamic bike data from JCD
# Need to add Open Weather scrapper to this file
import login
import pymysql
import requests
import time

# Add while loop

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

            # For each station, extract the following data points:
            for station in data:
                number = station.get('number')
                name = station.get('name')
                station_capacity = station.get('bike_stands')
                available_bike_stands = station.get('available_bike_stands')
                available_bikes = station.get('available_bikes')
                status = station.get('status')
                last_update = station.get('last_update')

                # Try insert this data into the static table.
                try:
                    sql_dynamic = 'INSERT INTO dynamic(number, name, bike_stands, available_bike_stands, available_bikes, status, last_update) VALUES(%s,%s,%s,%s,%s,%s,%s);'
                    dynamic_values = (number, name, station_capacity, available_bike_stands, available_bikes, status, last_update)
                    cursor.execute(sql_dynamic, dynamic_values)
                    conn.commit()

                    # Confirm rows added successfully
                    print("Rows inserted successfully!")

                except Exception as e:
                    print(f"Database error: {e}")
                    # Rollback any changes made to database if there was an error
                    conn.rollback() 

            # Close the connection
            cursor.close()
            conn.close()        
        else:
            print("Error: API request failed with status code", r.status_code)

    except pymysql.Error as e:
        print("Error connecting to database:", e)

    # Add 5 minute repeat.
    time.sleep(300)

