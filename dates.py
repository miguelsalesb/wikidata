"""
There are dates that are not precise and use qualifiers to get a greater range of 
- dates with 4 digits
- has question marks?
- has 'ca' (circa)?
- has 'fl' (flourished)?
- has 'fl' and 'ca'?
- has 'fl' and 'entre' (portuguese for 'between')?

The QIDs for the qualifiers are:
circa = Q5727902



"""

import re

dates = 'ca entre 1970-fl 2050'
qualifiers_dict = {}
dates_dict = {}
dates_list = []
qualifiers_list = []

qualifiers_qids = {'ca': 'Q5727902', 'fl': 'P1317'}


def get_dates(date):
    
    birth_date = 0
    death_date = 0

    if 'ca' in date and 'fl' not in date:
        ca = re.findall('(ca]+)', date)
        print(ca)

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


def get_qualifiers_list(dates, qualifiers=''):
    # Since there may be more than one qualifier in the birth or death dates
    # create a dictionnary with lists containing the qualifiers before and after the hifen

    find_qualifier = re.findall(f'({qualifiers})+|(-)', dates)
    
    qualifiers_before_hifen = []                
    qualifiers_after_hifen = []
    for i in range(len(find_qualifier)):
        for v in range(len(find_qualifier[i])):
            if len(find_qualifier[i][v]) > 0:
                qualifiers_list.append(find_qualifier[i][v])
        
    # Find where the hifen is located inside the list
    # to separate the birth and death dates
    hifen_index = qualifiers_list.index('-')    
    for i in range(len(qualifiers_list)):
        
        if i < hifen_index:
            qualifiers_before_hifen.append(qualifiers_list[i])
            qualifiers_dict['birth_date'] = qualifiers_before_hifen
        
        if i > hifen_index:
            qualifiers_after_hifen.append(qualifiers_list[i])
            qualifiers_dict['death_date'] = qualifiers_after_hifen

        if 'birth_date' not in qualifiers_dict:
            qualifiers_dict['birth_date'] = []

        if 'death_date' not in qualifiers_dict:
            qualifiers_dict['death_date'] = []

    
    return qualifiers_dict


def get_dates_list(dates):
    
    find_dates = re.findall(f'([0-9]+)|([-])|([0-9]+)', dates)
    
    for i in range(len(find_dates)):
        for v in range(len(find_dates[i])):
            if len(find_dates[i][v]) > 0:
                dates_list.append(find_dates[i][v])
    
    hifen_index = dates_list.index('-')
    
    for i in range(len(dates_list)):
        if i < hifen_index:
            dates_dict['birth_date'] = dates_list[i]
        
        if i > hifen_index:
            dates_dict['death_date'] = dates_list[i]

    return dates_dict



def get_qualifiers_positions():
    pass

test1 = get_qualifiers_list(dates, 'ca|fl|entre')
print(test1)
date1 = get_dates_list(dates)
print(date1)