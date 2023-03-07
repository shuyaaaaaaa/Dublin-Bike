from flask import Flask, render_template, request
import json
import mysql.connector
import login
import requests

app = Flask(__name__)

# Map Route (Index)
@app.route('/', methods=['GET', 'POST'])
def index():
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

    return render_template('index.html', data=json.dumps(data))

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
                        station_capacity = station.get('bike_stands')
                        available_bike_stands = station.get('available_bike_stands')
                        available_bikes = station.get('available_bikes')
                        status = station.get('status')
                        break
                
                # Response HTML for POST request
                text_response = f"""
                    <div id='detailed_info'>
                        <button id='close-button' class="close-button">&times;</button>
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

# Live station data on hover
@app.route('/hover', methods=['GET', 'POST'])
def hover():
    # ------ Station Information - Marker Hover ------- 

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
                        available_bike_stands = station.get('available_bike_stands')
                        available_bikes = station.get('available_bikes')
                        break
                
                # Response HTML for POST request
                text_response = f"<p>Bikes: {available_bikes} Stands: {available_bike_stands}</p>"
                    
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

if __name__ == '__main__':
    app.run(debug=True)
