# Dublin Bikes App 🚴

This Dublin Bikes App provides a comprehensive overview of bike availability and docking stations across Dublin, enriched with real-time weather data, route planning features, and future predictions for bike station data. The application, developed using Flask, leverages advanced machine learning algorithms and is hosted on AWS EC2 for seamless user experience.

![Dublin Bikes Map View](your_image_link_1.jpg)

## Features:

### 1. **Map View:**
Visualize the Dublin Bikes station network. Navigate through different areas of Dublin to find the nearest station.

### 2. **Bike Availability Visualization:**
See available bikes for your selected stand. The bike availability is represented by circle colors ranging from green (high availability) to red (low availability).

![Dublin Bikes Availability View](your_image_link_2.jpg)

### 3. **Stand Availability Visualization:**
See available stands for docking your bike. The stand availability is represented by circles ranging from big (high availability) to small (low availability).

### 4. **Weather Integration:**
Integrates with weather APIs to fetch real-time weather conditions in Dublin, including temperature, pressure, humidity, sunrise, and sunset times.

### 5. **Route Planning:**
Using the random-forest machine learning algorithm, the app provides predictions on bike availability based on past weather data and bike data. Red markers on the map represent available bikes at each station.

## Technical Details:

- **Backend Framework:** The app is built using Flask, a lightweight web application framework.
- **Machine Learning:** The bike availability prediction uses a random-forest algorithm with around 90% accuracy, trained on historical data to provide accurate forecasts.
- **Hosting:** The application is hosted on AWS EC2, ensuring high availability and scalability.
- **Database:** We use AWS RDS for data storage, allowing for efficient data retrieval and consistent performance.
- **API Integration:** The app integrates with various APIs, including weather data providers and Dublin bike data providers.

---

### Support:

If you encounter any issues or have feedback, please contact [your support email].
