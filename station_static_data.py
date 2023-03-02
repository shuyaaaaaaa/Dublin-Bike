# Script for scrapping static bike data from JCDecaux (intended to only be used once)
import login
import pymysql
import requests
import send_email

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
            contract_name = station.get('contract_name')
            name = station.get('name')
            address = station.get('address')
            position_lat = station.get('position').get('lat')
            position_lng = station.get('position').get('lng')
            banking = station.get('banking')
            bonus = station.get('bonus')

            # Try insert this data into the static table.
            try:
                sql_static = 'INSERT INTO static(number, contract_name, name, address, position_lat, position_lng, banking, bonus) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);'
                static_values = (number, contract_name, name, address, position_lat, position_lng, banking, bonus)
                cursor.execute(sql_static, static_values)
                conn.commit()

            except Exception as e:
                print(f"Database error: {e}")
                # Rollback any changes made to database if there was an error
                conn.rollback() 
                send_email.email_error(e)
        
        # Confirm rows added successfully
        print("Rows inserted successfully!")
     
    else:
        print("Error: API request failed with status code", r.status_code)

    # Close the connection
    cursor.close()
    conn.close()
        
except pymysql.Error as e:
    print("Error connecting to database:", e)
    send_email.email_error(e)

