from datetime import datetime

# dates = ['july-december', 'July-december', 'july', 'December', '07/01-08/09'
# dates = 'JUly-dEcemBer'
dates = '07/01/2023-08/09/2023'
dates = '07/01-08/09'
# dates = '07-08'

def parse_date(date):
    # ['07/01/2023', '08/09/2023']
    start, end = date.lower().split('-')
    start_date = '/'.join(getMDY(start))
    end_date = '/'.join(getMDY(end))
    return start_date, end_date

def getMDY(date_string):
    months = {'july': '07', 'december': '12'}
    date = date_string.split('/')
    month = months.get(date[0]) or date[0]
    day = next(iter(date[1:2]), '01')
    year = next(iter(date[2:3]), str(datetime.now().year))
    print(day)
    print(month)
    print(date, date[2:3])
    print("year: ", year)
    return month,day,year
print(parse_date(dates))
