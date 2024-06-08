import urllib.request, urllib.parse
import json, ssl
import time

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

global f_wikidata_errors
f_wikidata_errors = open(f'library_errors.txt', 'w')

def get_wikidata_id(name, record, articles=False):
    # Only make the search if there is any name
    if len(name ) > 0:
        # Had to quote and encode the name because of diacritics
        # Got the solution on: https://stackoverflow.com/questions/4389572/how-to-fetch-a-non-ascii-url-with-urlopen
        # https://docs.python.org/3/library/urllib.parse.html
        
        if articles == True:
            author_name = name.replace(' des ', ' ').replace(' de ', ' ').replace(' das ', ' ').replace(' da ', ' ').replace(' dos ', ' ').replace(' do ', ' ').replace(' as ', ' ').replace(' a ', ' ').replace(' e ', ' ').replace(' os ', ' ').replace(' o ', ' ').replace('"', '')
        else:
            author_name = name.replace('"', '')

        author_name = urllib.parse.quote(author_name)
        
        # Besides portuguese, search also for the wikidata_ids in english, since is a more widely used language
        languages = ['pt', 'en']
        
        wikidata_ids = []   
        # time.sleep(0.5) 
        for language in languages:
            
            url = 'https://query.wikidata.org/sparql?format=json&query=SELECT%20DISTINCT%20?item%20WHERE%20{?item%20wdt:P31%20wd:Q5.%20?item%20?label%20"' + author_name + '"@' + language + '%20FILTER(BOUND(?item)).%20SERVICE%20wikibase:label%20{bd:serviceParam%20wikibase:language%20%22' + language + '%22.}}'

            try:
                uh = urllib.request.urlopen(url, context=ctx)
            except urllib.error.HTTPError as e:
                print("\n\nHTTP (wikidata) Error : ", e)
                # return ''
                quit()
            except urllib.error.URLError as e:
                print("URL (wikidata) Error: ", e)
                # return ''
                quit()
            
            data = uh.read().decode('utf-8') # read - fornece os dados em utf-8 e converte para unicode para ser manipulado pela Python
            
            js = json.loads(data) # converte os dados que estão numa string em json
            
            if len(js['results']['bindings']) > 0:
                id = js['results']['bindings'][0]['item']['value']
                pos = id.rindex('/')
                wikidata_id = id[pos + 1:].strip()
                
                if len(wikidata_id) > 0:
                    wikidata_ids.append(wikidata_id)
                else:
                    wikidata_ids.append('')
                
                # Check if there are two items in the list
                # If there is one, return that item
                # If there are two and they are equal, return one
                # If they are different, write on the error report     
                if len(wikidata_ids) == 2:
                    if wikidata_ids[0] != wikidata_ids[1]:
                        f_wikidata_errors.write('The pt and en alias are different in record: ', record)
                        f_wikidata_errors.flush()
                    elif wikidata_ids[0] == wikidata_ids[1]:
                        return wikidata_ids[0]

                elif len(wikidata_ids) == 1:
                    if len(wikidata_ids[0] ) > 0:
                        return wikidata_ids[0]
                    else:
                        return wikidata_ids[1]
                else:
                    return ''
                    
            else:
                return ''
    else:
        return ''
    


# There are cases in which the Library and Wikidata wikidata_ids are of the same author
# but the name in Wikidata doesn't have articles
# The objective of this function, is to catch those cases
# def get_wikidata_id_from_name_without_articles(name, record):
#     # Only make the search if there is any name
#     if len(name ) > 0:
#         author_name = name.replace(' des ', ' ').replace(' de ', ' ').replace(' das ', ' ').replace(' da ', ' ').replace(' dos ', ' ').replace(' do ', ' ').replace(' as ', ' ').replace(' a ', ' ').replace(' e ', ' ').replace(' os ', ' ').replace(' o ', ' ').replace('"', '')

#         author_name = urllib.parse.quote(author_name)
#         languages = ['pt', 'en']
#         wikidata_ids = []
        
#         # time.sleep(0.5)
#         for language in languages:
#             url = 'https://query.wikidata.org/sparql?format=json&query=SELECT%20DISTINCT%20?item%20WHERE%20{?item%20wdt:P31%20wd:Q5.%20?item%20?label%20"' + author_name + '"@' + language + '%20FILTER(BOUND(?item)).%20SERVICE%20wikibase:label%20{bd:serviceParam%20wikibase:language%20%22' + language + '%22.}}'

#             try:
#                 uh = urllib.request.urlopen(url, context=ctx)
#             except urllib.error.HTTPError as e:
#                 print("\n\nHTTP (wikidata) Error : ", e)
#                 # return ''
#                 quit()
#             except urllib.error.URLError as e:
#                 print("URL (wikidata) Error: ", e)
#                 # return ''
#                 quit()
            
#             data = uh.read().decode('utf-8') # read - fornece os dados em utf-8 e converte para unicode para ser manipulado pela Python
#             # print('Retrieved', len(data), 'characters', data[:20].replace('\n', ' '))

#             js = json.loads(data) # converte os dados que estão numa string em json
#             if len(js['results']['bindings']) > 0:
#                 id = js['results']['bindings'][0]['item']['value']
#                 pos = id.rindex('/')
#                 wikidata_id = id[pos + 1:].strip()
                
#                 if len(wikidata_id) > 0:
#                     wikidata_ids.append(wikidata_id)
#                 else:
#                     wikidata_ids.append('')
                
#                 # Check if there are two items in the list
#                 # If there is one, return that item
#                 # If there are two and they are equal, return one
#                 # If they are different, write on the error report     
#                 if len(wikidata_ids) == 2:
#                     if wikidata_ids[0] != wikidata_ids[1]:
#                         f_wikidata_errors.write('The pt and en alias are different in record: ', record)
#                         f_wikidata_errors.flush()
#                     elif wikidata_ids[0] == wikidata_ids[1]:
#                         return wikidata_ids[0]

#                 elif len(wikidata_ids) == 1:
#                     if len(wikidata_ids[0] ) > 0:
#                         return wikidata_ids[0]
#                     else:
#                         return wikidata_ids[1]
#                 else:
#                     return ''
                    
#             else:
#                 return ''
#     else:
#         return ''

# get_wiki_id("Mario Soares", 11)


def get_wikidata_data(wikidata_id, library_id):
    
    # wikidata_author_description = ""
    wikidata_author_library_id = ""
    wikidata_author_birth_date = ""
    wikidata_author_death_date = ""
    wikidata_author_occupations = []
    wikidata_author_notable_work = []    
    
    url = 'https://query.wikidata.org/sparql?format=json&query=SELECT%20?prop%20?val_%20?val_Label%20?authorDescription%20{VALUES%20(?author)%20{(wd:' + wikidata_id + ')}%20?author%20?p%20?statement.%20?statement%20?val%20?val_.%20?prop%20wikibase:claim%20?p.%20?prop%20wikibase:statementProperty%20?val.%20SERVICE%20wikibase:label%20{bd:serviceParam%20wikibase:language%20%22pt%22%20}}%20ORDER%20BY%20?prop%20?statement%20?val_'

    try:
        uh = urllib.request.urlopen(url, context=ctx)
    except urllib.error.HTTPError as e:
        print("\n\nHTTP (wikidata) Error : ", e)
        quit()
    except urllib.error.URLError as e:
        print("URL (wikidata) Error: ", e)
        quit()
                
    data = uh.read().decode('utf-8') 
    js = json.loads(data)


    if len(js['results']['bindings']) > 0:
        
        for data in js['results']['bindings']:
            occupation = ""
            notable_work = ""
            for key, values in data.items():
                if key == 'prop' and values['value'] == 'http://www.wikidata.org/entity/P1005':
                    wikidata_author_library_id = data['val_Label']['value']
                
                if key == 'prop' and values['value'] == 'http://www.wikidata.org/entity/P569':
                    wikidata_author_birth_date = data['val_Label']['value']
                    
                if key == 'prop' and values['value'] == 'http://www.wikidata.org/entity/P570':
                    wikidata_author_death_date = data['val_Label']['value']
                   
                if key == 'prop' and values['value'] == 'http://www.wikidata.org/entity/P106':
                    for value in values:
                        occupation = data['val_Label']['value']
                if key == 'prop' and values['value'] == 'http://www.wikidata.org/entity/P800':
                    for value in values:
                         notable_work = data['val_Label']['value']                 

            if len(occupation) > 0:
                wikidata_author_occupations.append(occupation)
            if len(notable_work) > 0:
                wikidata_author_notable_work.append(notable_work)
    
    print("wikidata_author_notable_work: ", wikidata_author_notable_work)
    return {
            "wikidata_library_id": wikidata_author_library_id, 
            "wikidata_birth_date": wikidata_author_birth_date, 
            "wikidata_death_date": wikidata_author_death_date,
            "wikidata_notable_work": wikidata_author_notable_work
            }