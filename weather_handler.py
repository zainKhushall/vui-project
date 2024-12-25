import requests


class Weather_Handler:
    def get_weather(self, city, api_key):
            WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
            try:
                params = {
                    'q': city,
                    'appid': api_key,
                    'units': 'metric'  # Use metric units for temperature in Celsius
                }
                response = requests.get(WEATHER_API_URL, params=params)
                data = response.json()

                # Extract relevant information
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]

                weather_info = (
                    f"The current weather in {city} is {description} with a temperature of {temp}°C. "
                    f"Humidity is at {humidity}% and wind speed is {wind_speed} meter per second."
                )
                return  weather_info  # Structured response for ChatGPT
            except Exception as e:
                print("Error fetching weather data:", e)
                return {"weather_response": "Sorry, I couldn't fetch the weather data at the moment."}