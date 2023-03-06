from flask import Flask, render_template, request
import json
import mysql.connector
import login
import requests

app = Flask(__name__)

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
                        name = station.get('address')
                        station_capacity = station.get('bike_stands')
                        available_bike_stands = station.get('available_bike_stands')
                        available_bikes = station.get('available_bikes')
                        status = station.get('status')
                        break
                
                # Response HTML for POST request
                text_response = f"""
                    <h3 class='center'>{name} ({number})</h3>
                    <ul>
                        <li>Available Bikes: {available_bikes}</li>
                        <li>Available Stands: {available_bike_stands}</li>
                        <li>Capacity: {station_capacity}</li>
                    </ul>
                    <p class='center'>This station is: {status}</p>
                    <button id="close-button">Close</button>
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
    
    # Render the HTML page on load
    else:
        return render_template('index.html', data=json.dumps(data))

if __name__ == '__main__':
    app.run(debug=True)
