from flask import Flask, render_template, request, jsonify
import json
import mysql.connector
import login
import requests
import pickle
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

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

        # Connect to JCDecaux API for live station data: For marker hover
        r = requests.get(login.jcdUri, params={'contract':login.jcdName,
                                        'apiKey': login.jcdKey})

        if r.status_code == 200:
            # If connection successful:
            print('Connection to JCDecaux successful! Marker Station Data Incoming...')
            live_station_data = r.json()

        else:
            print('Error connecting to JCDecaux', r.status_code)

        return render_template('index.html', data=json.dumps(data), live_station_data=json.dumps(live_station_data))
    
    except Exception as e:
        print('Error connecting to database:', e)

# Detailed Information Display
@app.route('/detailed', methods=['GET', 'POST'])
def detailed():
    # ------ Deatiled Station Information ------- 
    # If POST request submitted:
    if request.method == 'POST':
        try:
        # Connect to JCDecaux API
            r = requests.get(login.jcdUri, params={'contract':login.jcdName,
                                            'apiKey': login.jcdKey})

            if r.status_code == 200:
                # If connection successful:
                print('Connection to JCDecaux successful!')
                data = r.json()

                # Extract station number POST request: 
                user_request = int(request.form['station_num'])
                print('Extracted station number =', user_request)
                
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

                #Get the prediction for this station:
                # Loading pickle file
                # de-serialize model.pkl file into an object called model using pickle
                ##feed in desired station number
                model_number = f'/datamodel/models/model_{number}.pkl'
                with open(model_number, 'rb') as handle:
                    model = pickle.load(handle)

                #X_test is the feature to query:
                #Should be in the form of: 
                #Day, hour and it will predict the number of bikes available at that station
                # up to 5 days in advance
                X_test=[[1, 12]]
                result = model.predict(X_test)
                
                # Response HTML for POST request
                text_response = f"""
                        <button id='close-button' class="close-button">&times;</button>

                        <div id='detailed_info'>
                            <h3 class=''>{name} ({number})</h3>
                            <h4 class=''>{address}</h3>
                            <div id='detailed_blocks'>
                                <div id='available_bikes' class='info_block'>
                                    <p>Bikes:</p>
                                    <p>{available_bikes}</p>
                                </div>
                                <div id='available_stands' class='info_block'>
                                    <p>Stands:</p>
                                    <p>{available_bike_stands}</p>
                                </div>
                            </div>
                            <div id='station_status'>
                                <p class='block_green'>This station is: {status}</p>

                            </div>
                            <div id='prediction'>
                                <p class='block_green'>Predicted bikes available at 12:00 on 04/03/2023: {result}</p>
                            </div>
                        </div>
                        
                """
                    
                try:
                    # Render the HTML with the extracted data points
                    return text_response
                except Exception as e:
                    print('Error displaying web page. Error: ', e)
                    
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
        route_data = {
            'start_lat': response_start['results'][0]['geometry']['location']['lat'],
            'start_lng': response_start['results'][0]['geometry']['location']['lng'],
            'end_lat': response_end['results'][0]['geometry']['location']['lat'],
            'end_lng': response_end['results'][0]['geometry']['location']['lng']
        }

        print('Route data to be returned:', route_data)

        return jsonify(route_data)
    

if __name__ == '__main__':
    app.run(debug=True)
