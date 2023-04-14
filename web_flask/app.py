from flask import Flask, render_template, request, jsonify
import json
import mysql.connector
import login
import requests
import pickle
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime
import math
import os

app = Flask(__name__)

# Map Route (Index)
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        # -------- Google Map View --------
        # Connect to the database & select static bike information
        conn = mysql.connector.connect(
            host=login.dbHost,
            user=login.dbUser,
            password=login.dbPassword,
            database=login.dbDatabase
        )
        cursor = conn.cursor()
        cursor.execute('SELECT position_lat, position_lng, name, number FROM static')
        data = cursor.fetchall()

         # Get current weather data for home page
        w = requests.get(login.owUri, params={'lat':login.owLat, 'lon':login.owLon, 'units':'metric', 'exclude': 'minutely,hourly,daily,alerts', 'appid':login.owKey})
        
        if w.status_code == 200:
            print('Connected to OpenWeather and data collected successfully')
            current_weather = w.json()

        wf=requests.get(login.owFor, params={'lat':login.owLat, 'lon':login.owLon, 'units':'metric','appid':login.owKey})#exclude more?

        if wf.status_code == 200:
            print('Connected to OpenWeather and collected forecast data successfully')
            forecast_weather = wf.json()        

        # Connect to JCDecaux API for live station data: For marker hover
        r = requests.get(login.jcdUri, params={'contract':login.jcdName,
                                        'apiKey': login.jcdKey})

        if r.status_code == 200:
            # If connection successful:
            print('Connection to JCDecaux successful! Marker Station Data Incoming...')
            live_station_data = r.json()

        else:
            print('Error connecting to JCDecaux', r.status_code)

        return render_template('index.html', data=json.dumps(data), live_station_data=json.dumps(live_station_data), current_weather=json.dumps(current_weather), forecast_weather=json.dumps(forecast_weather))
    
    except Exception as e:
        print('Error connecting to database:', e)

# Detailed Information Display
@app.route('/detailed', methods=['GET', 'POST'])
def detailed():
    # ------ Deatiled Station Information ------- 
    # If POST request submitted:
    if request.method == 'POST':
        try:
            try:
                # Connect to the database to extract historical data
                conn = mysql.connector.connect(
                    host=login.dbHost,
                    user=login.dbUser,
                    password=login.dbPassword,
                    database=login.dbDatabase
                )
            except Exception as e:
                    print('Error connecting to database. Error: ', e)

            # Find the current day
            current_day = datetime.now().strftime('%A')

            # Extract station number POST request: 
            user_request = int(request.form['station_num'])
            print('Extracted station number =', user_request)

            # Collect the bike data from the database
            # Use DAYNAME to extract only the rows that match the current day
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT bike_stands, available_bikes, available_bike_stands, s_date, s_time FROM dynamic WHERE number={} and DAYNAME(s_date) = \'{}\''.format(user_request, current_day))
                data = cursor.fetchall()
                print('Successfully extracted data')
            except Exception as e:
                    print('Error extracting database data. Error: ', e)

            # Calculate the average number of available bikes per hour for the current day across the data set
            # Extract and record the number of available bike at the start of each hour for each unique day
            # Add up the total number of available bikes for each hour
            # Divide by the total number of unique days
            # Plot the results
            try:
                # Calculate the total number of unique days
                # The total number of occurences of the current day in the data set
                total_days = set()
                for row in data:
                    if row[3] not in total_days:
                        total_days.add(row[3])

                num_total_days = len(total_days)
                
                average_bikes_stands_hours = {}
                visited_hours = {}    

                for row in data:
                    # For each row in the data set extract the hour and date
                    hour = int(row[4].total_seconds()//3600)
                    date = row[3]

                    # If the hour hasn't been recorded yet, add it to the average availability dictionary
                    if hour not in average_bikes_stands_hours:
                        average_bikes_stands_hours[hour] = {'T Bikes': 0, 'T Stands': 0}
                    
                    # If the date hasn't been seen yet, add it to the visited hours dictionary with an empty set
                    if date not in visited_hours:
                        visited_hours[date] = set()
                    
                    # If the hour has not been seen yet for the date, add the bike availability to the total
                    # Record that the hour has been seen for the date
                    if hour not in visited_hours[date]:
                        average_bikes_stands_hours[hour]['T Bikes'] += row[1]
                        average_bikes_stands_hours[hour]['T Stands'] += row[2]
                        visited_hours[date].add(hour)

                for hour, info in average_bikes_stands_hours.items():
                    average_availability = round(info['T Bikes'] / num_total_days)
                    info['Avg A'] = average_availability
                    average_occupancy = round(info['T Stands']/ num_total_days)
                    info['Avg O'] = average_occupancy
                
                print(average_bikes_stands_hours)


            except Exception as e:
                    print('Error calculating average availability. Error: ', e)

            # Connect to JCDecaux API
            r = requests.get(login.jcdUri, params={'contract':login.jcdName,
                                            'apiKey': login.jcdKey})

            if r.status_code == 200:
                # If connection successful:
                print('Connection to JCDecaux successful!')
                data = r.json()
                
                # For each station, extract the following data points:
                for station in data:
                    station_num = station.get('number')
                    if station_num == user_request:
                        number = station.get('number')
                        name = station.get('name')
                        address = station.get('address')
                        available_bike_stands = station.get('available_bike_stands')
                        available_bikes = station.get('available_bikes')
                        status = station.get('status')
                        break

                # Response HTML for POST request
                text_response = f"""
                        <button id='close-button' class="close-button">&times;</button>

                        <div id='detailed_info'>
                            <div class = "detailed_name">
                            <h3 class=''>{name} ({number})</h3>
                            <h4 class=''>{address}</h3>
                            </div>
                            <div id='detailed_blocks'>
                                <div id='available_bikes' class='info_block'>
                                    <p>Available Bikes:</p>
                                    <p><i class="fa-solid fa-bicycle"></i> {available_bikes}</p>
                                </div>
                                <div id='available_stands' class='info_block'>
                                    <p>Available Stands:</p>
                                    <p><i class="fa-solid fa-square-parking"></i> {available_bike_stands}</p>
                                </div>
                            </div>
                            <div id='station_status'>
                                <p class='block_green'>This station is: {status}</p>
                            </div>
                            <div class ="charts">
                            <div class ="chart-buttons">
                            <button class="chart-btn active" id="show-bikechart"><i class="fa-solid fa-bicycle"></i> Average Bikes</button>
                            <button class="chart-btn" id="show-stationchart"><i class="fa-solid fa-square-parking"></i> Average Spaces</button>
                            </div>
                            <div id='availability_chart'>
                                <canvas id="availabilityChart"></canvas>
                            </div>
                            <div id='occupancy_chart'>
                                <canvas id="occupancyChart"></canvas>
                            </div>
                            
                        </div>
                        <script>
                            var averageData = {json.dumps(average_bikes_stands_hours)};
                        </script>
                        
                """
                    
                try:
                    # Render the HTML with the extracted data points
                    return text_response
                except Exception as e:
                    print('Error displaying response. Error: ', e)
                    
            else:
                # If connection to JCDecaux fails, render an error message
                error_response = "<h4>Something went wrong. Please try again.</h4>"
                return error_response

        except Exception as e:
            print("Connection error:", e)

# Route Planner
@app.route('/route', methods=['GET', 'POST'])
def route():
    # -------- Cian Route Code ----------
    if request.method == 'POST':
        try:
            # Connect to the database & select static bike information
            conn = mysql.connector.connect(
                host=login.dbHost,
                user=login.dbUser,
                password=login.dbPassword,
                database=login.dbDatabase
            )
            cursor = conn.cursor()
            cursor.execute('SELECT position_lat, position_lng, name, number FROM static')
            data = cursor.fetchall()
        except Exception as e:
            print('Error connecting to database:', e)

        try:
            # Get the start and end locations from the form
            start = request.form['start']
            end = request.form['end']
            # Get the latitude and longitude of the start and end locations
            #by using the Google Maps Geocoding API
            apiKey='AIzaSyANu9D6AUdAajvwdweM-tkgx6CX1J9NdvQ'
            url_start = f'https://maps.googleapis.com/maps/api/geocode/json?address={start}&key={apiKey}'
            url_end = f'https://maps.googleapis.com/maps/api/geocode/json?address={end}&key={apiKey}'
            #parse the urls
            response_start = requests.get(url_start).json()
            response_end = requests.get(url_end).json()
            #get the lat and lng from the json data
            # store variables and values in a dictionary and return the dictionary. We can then extract the values in JavaScript.

            response_start_lat = response_start['results'][0]['geometry']['location']['lat']
            response_start_long = response_start['results'][0]['geometry']['location']['lng']
            response_end_lat = response_end['results'][0]['geometry']['location']['lat']
            response_end_long = response_end['results'][0]['geometry']['location']['lng']

            # Identify closest station to start and end and return updated route data with 'stops'
            # calculate the distance from the start point to each station - store in a dictionary
            # calculate the distance from the end point to each station - store in a dictionary
            # Extract the lat and long of the station with the shortest distance to the start
            # Extract the lat and long of the station with the shortest distance to the end
            # Return the route data incorporating the stations as 'stops'
 
            def haversine(lat1, lon1, lat2, lon2):
                # Convert latitude and longitude from degrees to radians
                lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
                # Haversine formula
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
                c = 2 * math.asin(math.sqrt(a))
                # Radius of the Earth in kilometers (use 3956 for miles)
                R = 6371
                # Calculate the distance
                distance = R * c
                return distance
            
            station_distances = {}

            for row in data:
                row_lat = row[0]
                row_long = row[1]
                station_num = row[3]  
                distance_start = haversine(response_start_lat, response_start_long, row_lat, row_long)
                distance_end = haversine(response_end_lat, response_end_long, row_lat, row_long)
                station_distances[station_num] = {'Distance Start': distance_start, 'Distance End': distance_end}
            
            min_distance_start = float('inf')
            min_distance_end = float('inf')
            min_start_station = None
            min_end_station = None

            for station_num, distances in station_distances.items():
                if distances['Distance Start'] < min_distance_start:
                    min_distance_start = distances['Distance Start']
                    min_start_station = station_num

                if distances['Distance End'] < min_distance_end:
                    min_distance_end = distances['Distance End']
                    min_end_station = station_num
            
            for row in data:
                if row[3] == min_start_station:
                    min_start_station_lat = row[0]
                    min_start_station_long = row[1]
                if row[3] == min_end_station:
                    min_end_station_lat = row[0]
                    min_end_station_long = row[1]

            print(f"The closest station to the start point is station {min_start_station} with a distance of {min_distance_start:.2f} kilometers.")
            print(f"The closest station to the end point is station {min_end_station} with a distance of {min_distance_end:.2f} kilometers.")

            route_data = {
                'start_lat': response_start_lat,
                'start_lng': response_start_long,
                'start_station_lat': min_start_station_lat,
                'start_station_long': min_start_station_long,
                'end_station_lat': min_end_station_lat,
                'end_station_long': min_end_station_long,
                'end_lat': response_end_lat,
                'end_lng': response_end_long
            }
        except Exception as e:
            print('Error getting route data:', e)
            # Perform Prediction

        #Get the station number from the form
        station_number_start = min_start_station
        station_number_end = min_end_station

        if 'X_test' in request.form:
            try:
                route_data['prediction'] = {}
                route_data['prediction']['start'] = station_number_start
                route_data['prediction']['end'] = station_number_end
                X_test = request.form['X_test']
                #Unstringify the X_test
                X_test=json.loads(X_test)

                #Load the model for that station
                model_start_station = os.path.join(app.static_folder, 'models', f'model_{station_number_start}.pkl')
                with open(model_start_station, 'rb') as handle:
                    model = pickle.load(handle)

                #X_test is the feature to query:
                #Should be in the form of: 
                #Day, hour and it will predict the number of bikes available at that station
                # up to 5 days in advance
                #X_test=[['temperature', 'wind_speed', 'rain', 'hour','Sunday','Monday', 
                #           'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']]

                #Get the prediction
                prediction = model.predict(X_test)
                #Return the prediction
                #converrt it to a string
                prediction = np.array2string(prediction)
                #remove the square brackets
                prediction = prediction.replace('[', '')
                prediction = prediction.replace(']', '')
                prediction = int(prediction)
                route_data['prediction']['predBikes'] = prediction

                model_end_station = os.path.join(app.static_folder, 'models', f'model_{station_number_end}.pkl')
                with open(model_end_station, 'rb') as handle:
                    model = pickle.load(handle)

                #Repeat for closest end station

                prediction = model.predict(X_test)
                prediction = np.array2string(prediction)
                prediction = prediction.replace('[', '')
                prediction = prediction.replace(']', '')
                stand_prediction = 100 - int(prediction)
                route_data['prediction']['predStands'] = stand_prediction

                print('Route and prediction data to be returned:', route_data)
            except Exception as e:
                print('Error getting prediction:', e)
        else:
            print('Route data to be returned:', route_data)
            
        return jsonify(route_data)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        #Get the station number from the form
        station_number = request.form['station_selected']
        #unstringify the station number
        station_number = int(station_number)
        X_test = request.form['X_test']
        #Unstringify the X_test
        X_test=json.loads(X_test)
        #Load the model for that station
        model_start_station = os.path.join(app.static_folder, 'models', f'model_{station_number}.pkl')
        with open(model_start_station, 'rb') as handle:
            model = pickle.load(handle)

        #X_test is the feature to query:
        #Should be in the form of: 
        #Day, hour and it will predict the number of bikes available at that station
        # up to 5 days in advance
        #X_test=[['temperature', 'wind_speed', 'rain', 'hour','Sunday','Monday', 
        #           'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']]

        #Get the prediction
        prediction = model.predict(X_test)
        #Return the prediction
        #converrt it to a string
        prediction = np.array2string(prediction)
        #remove the square brackets
        prediction = prediction.replace('[', '')
        prediction = prediction.replace(']', '')
        bike_predicition = int(prediction)
        stand_prediction = 100 - bike_predicition
        predictions = {}
        predictions['Bikes'] = bike_predicition
        predictions['Stands'] = stand_prediction
        json_predictions = json.dumps(predictions)
        return json_predictions
    
if __name__ == '__main__':
    app.run(debug=True)
