#Author: Andres Ortiz
#Description: Uses Weather.gov API service to retrieve information at sites

import requests
import Formulas.water_vapor_density as WVD

def get_weather_data(latitude, longitude, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    else:
        print("Failed to fetch weather data.")
        return None

def extract_weather_info(weather_data):
    if weather_data:
        pressure = weather_data["main"]["pressure"]  # Barometric pressure in hPa
        humidity = weather_data["main"]["humidity"]  # Humidity in percentage
        humidity = humidity/100
        temperature = weather_data["main"]["temp"]   # Temperature in Kelvin

        water_vapor_density = WVD.getWaterVaporDensity(humidity, temperature) #g/m^3

        return pressure, water_vapor_density, temperature
    else:
        return None, None, None





def loadAPIkey():
    filepath = "./api_key"
    with open(filepath, "r") as file:
        key = file.readline()
    return key

if __name__ == "__main__":
    latitude = 44.34   # Replace with your desired latitude
    longitude = 10.99  # Replace with your desired longitude
    api_key = loadAPIkey() 

    weather_data = get_weather_data(latitude, longitude, api_key)
    pressure, water_vapor_density, temperature = extract_weather_info(weather_data)

    if pressure and water_vapor_density and temperature:
        print(f"Barometric Pressure: {pressure} hPa")
        print(f"Water Vapor Density: {water_vapor_density} g/m^3")
        print(f"Temperature: {temperature} °K")
    else:
        print("Failed to get weather data.")
