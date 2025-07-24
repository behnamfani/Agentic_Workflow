import requests
import fastmcp

loc = "London"
url = f"https://wttr.in/{loc}?format=j1"
response = requests.get(url, timeout=20)
weather_data = response.json()
area = weather_data["nearest_area"][0]
area_name = area["areaName"][0]["value"]
country = area["country"][0]["value"]
region = area.get("region", [{"value": ""}])[0]["value"]

location_str = f"{area_name}"
if region and region != area_name:
    location_str += f", {region}"
location_str += f", {country}"

forecast_report = f"📅 **{3}-Day Weather Forecast for {location_str}**\n\n"

for i, day in enumerate(weather_data["weather"][:3]):
    date = day["date"]
    max_temp_c = day["maxtempC"]
    max_temp_f = day["maxtempF"]
    min_temp_c = day["mintempC"]
    min_temp_f = day["mintempF"]

    # Get the most representative weather description (usually around midday)
    hourly = day["hourly"]
    midday_weather = hourly[len(hourly)//2] if hourly else hourly[0]
    weather_desc = midday_weather["weatherDesc"][0]["value"]

    day_label = "Today" if i == 0 else ("Tomorrow" if i == 1 else date)

    forecast_report += f"**{day_label} ({date}):**\n"
    forecast_report += f"🌡️ High: {max_temp_c}°C ({max_temp_f}°F) | Low: {min_temp_c}°C ({min_temp_f}°F)\n"
    forecast_report += f"☁️ {weather_desc}\n\n"

print(forecast_report)