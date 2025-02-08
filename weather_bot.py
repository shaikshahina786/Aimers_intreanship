import telebot
import requests

# Replace with your own Telegram API key
TELEGRAM_API_KEY = 'add your telegram api key'
WEATHER_API_KEY = '1daabf67352aa3867aaed054a03e460e'  # OpenWeatherMap API Key

bot = telebot.TeleBot(TELEGRAM_API_KEY)

# Command: /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "🌤 Hello! I am your Weather Bot.\n"
        "Type /weather <city_name> to get the current weather report.\n"
        "Example: /weather London"
    )

# Command: /weather
@bot.message_handler(commands=['weather'])
def get_weather(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "⚠️ Please provide a city name. Usage: /weather <city_name>")
        return

    city = parts[1].strip()
    weather_data = fetch_weather(city)

    if 'error' in weather_data:
        bot.send_message(message.chat.id, f"❌ Error: {weather_data['error']}")
    else:
        bot.send_message(
            message.chat.id,
            f"🌍 Weather in {weather_data['city']}:\n"
            f"🌡 Temperature: {weather_data['temperature']}°C\n"
            f"☁️ Condition: {weather_data['condition']}\n"
            f"💧 Humidity: {weather_data['humidity']}%\n"
            f"🌬 Wind Speed: {weather_data['wind_speed']} m/s"
        )

# Fetch weather data from OpenWeatherMap
def fetch_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={WEATHER_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return {"error": data.get("message", "Unable to fetch weather data.")}

        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "condition": data["weather"][0]["description"].capitalize(),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
        }
        return weather
    except Exception as e:
        return {"error": str(e)}

# Start polling
bot.polling()
