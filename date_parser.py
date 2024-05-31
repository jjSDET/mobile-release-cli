from datetime import datetime

def parse_single_date(date_str, current_year):
    parts = date_str.split('/')
    month = int(parts[0])
    day = int(parts[1]) if len(parts) > 1 else 1
    year = int(parts[2]) if len(parts) > 2 else current_year
    return datetime(year, month, day)

def parse_date_range(date_range, current_year):
    start_str, end_str = map(str.strip, date_range.split('-'))
    start = parse_single_date(start_str, current_year)
    end = parse_single_date(end_str, current_year)
    if end.month < start.month:
        end = end.replace(year=end.year + 1)
    return start, end

def parse_date(date_string, current_year):
    if '-' in date_string:
        return parse_date_range(date_string, current_year)
    else:
        single_date = parse_single_date(date_string, current_year)
        return single_date, single_date
