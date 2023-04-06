from flask import Flask, render_template, request, jsonify
import json
import mysql.connector
import login
import requests
from datetime import datetime

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
            

            # take the current day
            # display average number of available bikes by hour
            # display average number of stands by hour

            # take the current date, determine the day, go back 7 until you can't anymore
            #
            # take all the wed in the database
            # calculate

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
                            <h3 class=''>{name} ({number})</h3>
                            <h4 class=''>{address}</h3>
                            <div id='detailed_blocks'>
                                <div id='available_bikes' class='info_block'>
                                    <p>Available Bikes:</p>
                                    <p>{available_bikes}</p>
                                </div>
                                <div id='available_stands' class='info_block'>
                                    <p>Available Stands:</p>
                                    <p>{available_bike_stands}</p>
                                </div>
                            </div>
                            <div id='station_status'>
                                <p class='block_green'>This station is: {status}</p>
                            </div>
                            <div id='availability_chart'>
                                <canvas id="availabilityChart"></canvas>
                            </div>
                            <div id='occupancy_chart'>
                                <canvas id="occupancyChart"></canvas>
                            </div>
                        </div>
                        <script>
                            const averageData = {json.dumps(average_bikes_stands_hours)};
                            generateAvailabilityChart(averageData);
                            generateOccupancyChart(averageData)
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
