import re


def get_dates(date):
    
    birth_date = 0
    death_date = 0

    try:
        dates = re.findall('([0-9]{4})-([0-9]{4})', date)
    except:
        return '', ''
    
    try:
        birth_date = int(dates[0][0])
    except:
        birth_date = 0

    try:
        death_date = int(dates[0][1])
    except:
        death_date = 0
    
    return birth_date, death_date