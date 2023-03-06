from flask import Flask, render_template, request
import pymysql
import login2
import requests

# Connect to JCD
# Extract data
# Display data on html page

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/', methods=['GET', 'POST'])
def index():
    # If form submitted (POST request)
    if request.method == 'POST':
        try:
        # Connect to JCDecaux API
            r = requests.get(login2.jcdUri, params={'contract':login2.jcdName,
                                            'apiKey': login2.jcdKey})

            if r.status_code == 200:
                # If connection successful:
                print('Connection to JCDecaux successful!')
                data = r.json()

                # Only for the purpose of this test file: create a set of all station numbers to check form input against
                check_station = set()
                for station in data:
                    check_station.add(station.get('number'))

                # Extract station number from HTML form
                user_request = int(request.form['station_number'])
                
                # If the station number exists:
                if user_request in check_station:
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
                    # Render the HTML page with the extracted data points
                    return text_response
                except Exception as e:
                    print('Error displaying web page. Error: ', e)

            # If the station does not exists, render the HTML page with an error message
            else:
                error_message = 'This station does not exist.'
                return render_template('detailed.html',
                                        error = error_message)

        except pymysql.Error as e:
            print("Error connecting to database:", e)
    
    # Render the HTML page on load
    else:
        return render_template('detailed.html')

if __name__ == '__main__':
    app.run()



    







