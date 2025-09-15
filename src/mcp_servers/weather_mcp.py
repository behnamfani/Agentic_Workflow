import requests
from fastmcp import FastMCP
from datetime import datetime, timedelta
import json

weather_mcp = FastMCP("Weather MCP")


def get_weather_data(loc: str):
    """Helper function to fetch weather data from wttr.in API"""
    try:
        url = f"https://wttr.in/{loc}?format=j1"
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch weather data: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse weather data: {e}")


def format_location(weather_data):
    """Helper function to format location string"""
    area = weather_data["nearest_area"][0]
    area_name = area["areaName"][0]["value"]
    country = area["country"][0]["value"]
    region = area.get("region", [{"value": ""}])[0]["value"]

    location_str = f"{area_name}"
    if region and region != area_name:
        location_str += f", {region}"
    location_str += f", {country}"

    return location_str


def get_weather_emoji(weather_desc):
    """Helper function to get appropriate weather emoji"""
    desc_lower = weather_desc.lower()
    if "sunny" in desc_lower or "clear" in desc_lower:
        return "☀️"
    elif "partly cloudy" in desc_lower:
        return "⛅"
    elif "cloudy" in desc_lower or "overcast" in desc_lower:
        return "☁️"
    elif "rain" in desc_lower or "drizzle" in desc_lower:
        return "🌧️"
    elif "thunderstorm" in desc_lower or "thunder" in desc_lower:
        return "⛈️"
    elif "snow" in desc_lower:
        return "❄️"
    elif "fog" in desc_lower or "mist" in desc_lower:
        return "🌫️"
    elif "wind" in desc_lower:
        return "💨"
    else:
        return "🌤️"


@weather_mcp.tool
def get_current_weather(loc: str):
    """
    Get the current weather conditions with detailed information
    :param loc: Location string (city, coordinates, etc.)
    :return: Current weather details
    """
    try:
        weather_data = get_weather_data(loc)
        print(weather_data)
        location_str = format_location(weather_data)
        print(location_str)

        current = weather_data["current_condition"][0]

        temp_c = current["temp_C"]
        temp_f = current["temp_F"]
        feels_like_c = current["FeelsLikeC"]
        feels_like_f = current["FeelsLikeF"]
        humidity = current["humidity"]
        pressure = current["pressure"]
        visibility = current["visibility"]
        wind_speed_kmh = current["windspeedKmph"]
        wind_speed_mph = current["windspeedMiles"]
        wind_dir = current["winddir16Point"]
        weather_desc = current["weatherDesc"][0]["value"]
        uv_index = current["uvIndex"]

        weather_emoji = get_weather_emoji(weather_desc)

        current_report = f"🌍 **Current Weather for {location_str}**\n\n"
        current_report += f"{weather_emoji} **{weather_desc}**\n\n"
        current_report += f"🌡️ **Temperature:** {temp_c}°C ({temp_f}°F)\n"
        current_report += f"🤚 **Feels Like:** {feels_like_c}°C ({feels_like_f}°F)\n"
        current_report += f"💧 **Humidity:** {humidity}%\n"
        current_report += f"🌬️ **Wind:** {wind_speed_kmh} km/h ({wind_speed_mph} mph) {wind_dir}\n"
        current_report += f"📊 **Pressure:** {pressure} mb\n"
        current_report += f"👁️ **Visibility:** {visibility} km\n"
        current_report += f"☀️ **UV Index:** {uv_index}\n"

        return current_report

    except Exception as e:
        return f"Error getting current weather: {e}"


@weather_mcp.tool
def get_weather_forecast(loc: str, days: int = 3):
    """
    Get the weather forecast for a specified number of days (1-3 days available)
    :param loc: Location string (city, coordinates, etc.)
    :param days: Number of days for forecast (1-3)
    :return: Weather forecast
    """
    try:
        if days < 1 or days > 3:
            return "Error: Number of days must be between 1 and 3"

        weather_data = get_weather_data(loc)
        location_str = format_location(weather_data)

        forecast_report = f"📅 **{days}-Day Weather Forecast for {location_str}**\n\n"

        for i, day in enumerate(weather_data["weather"][:days]):
            date = day["date"]
            max_temp_c = day["maxtempC"]
            max_temp_f = day["maxtempF"]
            min_temp_c = day["mintempC"]
            min_temp_f = day["mintempF"]

            # Get the most representative weather description (around midday)
            hourly = day["hourly"]
            midday_weather = hourly[len(hourly) // 2] if hourly else hourly[0]
            weather_desc = midday_weather["weatherDesc"][0]["value"]
            weather_emoji = get_weather_emoji(weather_desc)

            # Additional details
            avg_humidity = sum(int(h["humidity"]) for h in hourly) // len(hourly)
            avg_wind = sum(int(h["windspeedKmph"]) for h in hourly) // len(hourly)

            day_label = "Today" if i == 0 else ("Tomorrow" if i == 1 else f"Day {i + 1}")

            forecast_report += f"**{day_label} ({date}):**\n"
            forecast_report += f"{weather_emoji} {weather_desc}\n"
            forecast_report += f"🌡️ High: {max_temp_c}°C ({max_temp_f}°F) | Low: {min_temp_c}°C ({min_temp_f}°F)\n"
            forecast_report += f"💧 Avg Humidity: {avg_humidity}%\n"
            forecast_report += f"🌬️ Avg Wind: {avg_wind} km/h\n\n"

        return forecast_report

    except Exception as e:
        return f"Error getting weather forecast: {e}"


@weather_mcp.tool
def get_hourly_weather(loc: str, day: int = 0):
    """
    Get hourly weather forecast for a specific day
    :param loc: Location string (city, coordinates, etc.)
    :param day: Day number (0=today, 1=tomorrow, 2=day after tomorrow)
    :return: Hourly weather forecast
    """
    try:
        if day < 0 or day > 2:
            return "Error: Day must be 0 (today), 1 (tomorrow), or 2 (day after tomorrow)"

        weather_data = get_weather_data(loc)
        location_str = format_location(weather_data)

        if day >= len(weather_data["weather"]):
            return f"Error: Hourly data not available for day {day}"

        day_data = weather_data["weather"][day]
        date = day_data["date"]
        day_label = "Today" if day == 0 else ("Tomorrow" if day == 1 else f"Day after tomorrow")

        hourly_report = f"🕐 **Hourly Weather for {location_str} - {day_label} ({date})**\n\n"

        for hour_data in day_data["hourly"]:
            time = f"{hour_data['time']:0>4}"
            time_formatted = f"{time[:2]}:{time[2:]}"
            temp_c = hour_data["tempC"]
            temp_f = hour_data["tempF"]
            weather_desc = hour_data["weatherDesc"][0]["value"]
            humidity = hour_data["humidity"]
            wind_speed = hour_data["windspeedKmph"]
            wind_dir = hour_data["winddir16Point"]
            precipitation = hour_data["precipMM"]

            weather_emoji = get_weather_emoji(weather_desc)

            hourly_report += f"**{time_formatted}:** {weather_emoji} {temp_c}°C ({temp_f}°F) - {weather_desc}\n"
            hourly_report += f"   💧 Humidity: {humidity}% | 🌬️ Wind: {wind_speed} km/h {wind_dir}"

            if float(precipitation) > 0:
                hourly_report += f" | 🌧️ Precipitation: {precipitation}mm"

            hourly_report += "\n\n"

        return hourly_report

    except Exception as e:
        return f"Error getting hourly weather: {e}"


@weather_mcp.tool
def get_weather_summary(loc: str):
    """
    Get a comprehensive weather summary including current conditions and 3-day forecast
    :param loc: Location string (city, coordinates, etc.)
    :return: Complete weather summary
    """
    try:
        weather_data = get_weather_data(loc)
        location_str = format_location(weather_data)

        # Current weather
        current = weather_data["current_condition"][0]
        temp_c = current["temp_C"]
        temp_f = current["temp_F"]
        weather_desc = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        wind_speed = current["windspeedKmph"]

        weather_emoji = get_weather_emoji(weather_desc)

        summary = f"🌍 **Weather Summary for {location_str}**\n\n"
        summary += f"**Current Conditions:**\n"
        summary += f"{weather_emoji} {weather_desc}, {temp_c}°C ({temp_f}°F)\n"
        summary += f"Humidity: {humidity}%, Wind: {wind_speed} km/h\n\n"

        # 3-day outlook
        summary += f"**3-Day Outlook:**\n"
        for i, day in enumerate(weather_data["weather"][:3]):
            date = day["date"]
            max_temp = day["maxtempC"]
            min_temp = day["mintempC"]

            hourly = day["hourly"]
            midday_weather = hourly[len(hourly) // 2] if hourly else hourly[0]
            day_desc = midday_weather["weatherDesc"][0]["value"]
            day_emoji = get_weather_emoji(day_desc)

            day_label = "Today" if i == 0 else ("Tomorrow" if i == 1 else "Day 3")
            summary += f"• **{day_label}:** {day_emoji} {day_desc}, {min_temp}-{max_temp}°C\n"

        return summary

    except Exception as e:
        return f"Error getting weather summary: {e}"


@weather_mcp.tool
def get_weather_alerts(loc: str):
    """
    Get weather alerts and warnings for the location (if available)
    :param loc: Location string (city, coordinates, etc.)
    :return: Weather alerts information
    """
    try:
        weather_data = get_weather_data(loc)
        location_str = format_location(weather_data)

        # Check for extreme conditions in current and forecast data
        alerts = []

        # Check current conditions
        current = weather_data["current_condition"][0]
        temp_c = int(current["temp_C"])
        wind_speed = int(current["windspeedKmph"])
        uv_index = int(current["uvIndex"])

        if temp_c >= 35:
            alerts.append("🌡️ **Heat Warning:** Very high temperature detected")
        elif temp_c <= -10:
            alerts.append("❄️ **Cold Warning:** Very low temperature detected")

        if wind_speed >= 50:
            alerts.append("💨 **Wind Warning:** Strong winds detected")

        if uv_index >= 8:
            alerts.append("☀️ **UV Warning:** Very high UV index - sun protection recommended")

        # Check forecast for extreme conditions
        for i, day in enumerate(weather_data["weather"][:3]):
            max_temp = int(day["maxtempC"])
            min_temp = int(day["mintempC"])

            if max_temp >= 35:
                day_name = "today" if i == 0 else ("tomorrow" if i == 1 else "day after tomorrow")
                alerts.append(f"🌡️ **Heat Advisory:** High temperatures expected {day_name}")
            elif min_temp <= -10:
                day_name = "today" if i == 0 else ("tomorrow" if i == 1 else "day after tomorrow")
                alerts.append(f"❄️ **Freeze Warning:** Very cold temperatures expected {day_name}")

        alert_report = f"⚠️ **Weather Alerts for {location_str}**\n\n"

        if alerts:
            for alert in alerts:
                alert_report += f"{alert}\n"
        else:
            alert_report += "✅ No weather alerts or warnings at this time.\n"

        return alert_report

    except Exception as e:
        return f"Error getting weather alerts: {e}"


if __name__ == "__main__":
    weather_mcp.run(transport="stdio")