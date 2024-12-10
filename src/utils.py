from datetime import datetime, timedelta, timezone
import logging


# Ensure the logger is set up
logger = logging.getLogger("gmail_processor")

def parse_date_time(date_string):
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",  # Date with timezone offset
        "%a, %d %b %Y %H:%M:%S %Z",  # Date with named timezone
        "%a, %d %b %Y %H:%M:%S"      # Date without timezone
    ]
    
    cleaned_date = date_string.split('(')[0].strip()  # Remove anything in parentheses

    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned_date, fmt)
            if fmt == "%a, %d %b %Y %H:%M:%S":  # Add UTC for no timezone
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue  # Try the next format

    logger.error(f"Failed to parse date: {date_string}")
    return None




def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def compare_dates(date1, date2, operator, unit, value):
    if unit == 'days':
        delta = timedelta(days=value)
    elif unit == 'months':
        delta = timedelta(days=value * 30)
    else:
        return False

    if operator == 'less than':
        return date1 < date2 + delta
    elif operator == 'greater than':
        return date1 > date2 + delta
    return False
