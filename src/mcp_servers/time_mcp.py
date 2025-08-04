from typing import Optional
from fastmcp import FastMCP
from datetime import datetime, timedelta
import pytz
import time

time_mcp = FastMCP("Time MCP")


@time_mcp.tool
def get_time() -> str:
    """
    Get the current time. No input parameters required.
    """
    try:
        return f"The current time is {datetime.now().strftime('%H:%M:%S')}"
    except Exception as e:
        return f"Error occurred: {str(e)}"


@time_mcp.tool
def get_unix_timestamp() -> str:
    """
    Get the current Unix timestamp.
    """
    try:
        timestamp = int(time.time())
        return f"Current Unix timestamp: {timestamp}"
    except Exception as e:
        return f"Error getting timestamp: {str(e)}"


@time_mcp.tool
def convert_timestamp_to_date(timestamp: int) -> str:
    """
    Convert a Unix timestamp to human-readable date and time.
    :param timestamp: Unix timestamp (seconds since epoch)
    Send the input as {'timestamp': timestamp_int_value}
    """
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return f"Timestamp {timestamp} converts to: {dt.strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception as e:
        return f"Error converting timestamp: {str(e)}"


@time_mcp.tool()
def world_clock_dashboard() -> str:
    """
    Display current time across multiple timezones in a dashboard format.
    Can be used to find time in other locations.
    No input parameters required.
    """
    try:
        timezone_mapping = {
            "new york": "America/New_York",
            "london": "Europe/London",
            "tokyo": "Asia/Tokyo",
            "paris": "Europe/Paris",
            "sydney": "Australia/Sydney",
            "los angeles": "America/Los_Angeles",
            "chicago": "America/Chicago",
            "dubai": "Asia/Dubai",
            "mumbai": "Asia/Kolkata",
            "singapore": "Asia/Singapore",
            "berlin": "Europe/Berlin",
            "moscow": "Europe/Moscow",
            "beijing": "Asia/Shanghai",
            "cairo": "Africa/Cairo",
            "mexico city": "America/Mexico_City",
            "toronto": "America/Toronto",
            "vancouver": "America/Vancouver",
            "hong kong": "Asia/Hong_Kong",
            "bangkok": "Asia/Bangkok",
            "rome": "Europe/Rome",
            "madrid": "Europe/Madrid",
            "stockholm": "Europe/Stockholm",
            "amsterdam": "Europe/Amsterdam",
            "zurich": "Europe/Zurich",
            "istanbul": "Europe/Istanbul",
            "sao paulo": "America/Sao_Paulo",
            "buenos aires": "America/Argentina/Buenos_Aires"
        }
        selected_cities = timezone_mapping.keys()

        result = "🌍 WORLD CLOCK DASHBOARD\n"
        result += "=" * 50 + "\n\n"
        utc_time = datetime.now(pytz.UTC)
        result += f"🕐 UTC Time: {utc_time.strftime('%H:%M:%S')} ({utc_time.strftime('%Y-%m-%d')})\n\n"
        # Track if it's business hours (9 AM - 6 PM, Monday-Friday)
        for city in selected_cities:
            city_lower = city.lower().strip()
            timezone_str = timezone_mapping.get(city_lower)
            try:
                tz = pytz.timezone(timezone_str)
                local_time = utc_time.astimezone(tz)
                # Determine if it's business hours
                is_weekday = local_time.weekday() < 5  # Monday = 0, Friday = 4
                is_business_hours = 9 <= local_time.hour < 18
                is_business_time = is_weekday and is_business_hours

                # Create status indicator
                if is_business_time:
                    status = "✅ OPEN"
                elif is_weekday:
                    status = "❌ AFTER HOURS"
                else:
                    status = "🔴 WEEKEND"
                # Format day of week
                day_name = local_time.strftime('%a')
                # Time display with timezone
                time_str = local_time.strftime('%H:%M:%S')
                tz_abbr = local_time.strftime('%Z')
                date_str = local_time.strftime('%m/%d')
                result += f"🏙️  {city.title():<15} {time_str} {tz_abbr:<4} ({day_name} {date_str}) {status}\n"

            except Exception as e:
                result += f"❌ {city}: Error - {str(e)}\n"

        # Add time zone differences from UTC
        result += "\n🌐 UTC OFFSETS:\n"
        for city in selected_cities:
            city_lower = city.lower().strip()
            timezone_str = timezone_mapping.get(city_lower)

            if timezone_str:
                try:
                    tz = pytz.timezone(timezone_str)
                    local_time = utc_time.astimezone(tz)
                    offset_hours = local_time.utcoffset().total_seconds() / 3600
                    result += f"   {city.title()}: UTC{offset_hours:+.0f}\n"
                except:
                    continue

        return result

    except Exception as e:
        return f"Error creating world clock dashboard: {str(e)}"


# @time_mcp.tool
def calculate_age(birth_date: str, target_date: Optional[str] = None) -> str:
    """
    Calculate exact age in various units (years, months, days, hours, minutes, seconds).
    :param birth_date: Birth date in YYYY-MM-DD format (e.g., "1990-05-15")
    :param target_date: Optional target date in YYYY-MM-DD format (defaults to today)
    Send input as {'birth_date': 'birth_date_value', 'target_date': 'target_date_value'}
    :return: summary and facts about age
    """
    try:
        # Parse birth date
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        if target_date:
            target = datetime.strptime(target_date, "%Y-%m-%d")
        else:
            target = datetime.now()
        # Ensure target is after birth
        if target < birth:
            return "Error: Target date cannot be before birth date."
        # Calculate differences
        age_delta = target - birth
        # Calculate years and months more precisely
        years = target.year - birth.year
        months = target.month - birth.month
        # Adjust for cases where we haven't reached the birth month/day yet
        if target.month < birth.month or (target.month == birth.month and target.day < birth.day):
            years -= 1
            months += 12
        if target.day < birth.day:
            months -= 1
        # Calculate total units
        total_days = age_delta.days
        total_hours = total_days * 24 + (target.hour - birth.hour)
        total_minutes = total_hours * 60 + (target.minute - birth.minute)
        total_seconds = total_minutes * 60 + (target.second - birth.second)
        # Calculate weeks
        total_weeks = total_days // 7
        # Format the response
        comparison_date = target_date if target_date else "today"
        result = f"Age calculation from {birth_date} to {comparison_date}:\n\n"
        result += f"📅 Precise Age:\n"
        result += f"   {years} years, {months} months\n\n"
        result += f"🔢 Total Time Lived:\n"
        result += f"   Years: {years:,}\n"
        result += f"   Months: {years * 12 + months:,}\n"
        result += f"   Weeks: {total_weeks:,}\n"
        result += f"   Days: {total_days:,}\n"
        result += f"   Hours: {total_hours:,}\n"
        result += f"   Minutes: {total_minutes:,}\n"
        result += f"   Seconds: {total_seconds:,}\n\n"
        # Add some fun facts
        result += f"🎉 Fun Facts:\n"
        result += f"   You've lived through {total_days // 365} New Year's celebrations!\n"
        result += f"   You've seen about {total_days // 7:.0f} weekends!"

        return result

    except ValueError as e:
        return f"Error: Invalid date format. Use YYYY-MM-DD format (e.g., '1990-05-15'). Details: {str(e)}"
    except Exception as e:
        return f"Error calculating age: {str(e)}"


if __name__ == "__main__":
    time_mcp.run(transport="stdio")
    # print(calculate_age('1996-11-24'))