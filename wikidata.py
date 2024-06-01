import urllib.request, urllib.parse
import json, ssl
import time

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

global f_wikidata_errors
f_wikidata_errors = open(f'library_errors.txt', 'w')

def get_wiki_id(name, record):
    # Only make the search if there is any name
    if len(name ) > 0:
        # Had to quote and encode the name because of diacritics
        # Got the solution on: https://stackoverflow.com/questions/4389572/how-to-fetch-a-non-ascii-url-with-urlopen
        # https://docs.python.org/3/library/urllib.parse.html
        author_name = name.replace('"', '')

        author_name = urllib.parse.quote(author_name)
        
        # Besides portuguese, search also for the qids in english, since is a more widely used language
        languages = ['pt', 'en']
        
        qids = []   
            
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
                
                qid = id[pos + 1:].strip()
                
                if len(qid) > 0:
                    qids.append(qid)
                else:
                    qids.append('')
                
                # Check if there are two items in the list
                # If there is one, return that item
                # If there are two and they are equal, return one
                # If they are different, write on the error report     
                if len(qids) == 2:
                    if qids[0] != qids[1]:
                        f_wikidata_errors.write('The pt and en alias are different in record: ', record)
                        f_wikidata_errors.flush()
                    elif qids[0] == qids[1]:
                        return qids[0]

                elif len(qids) == 1:
                    if len(qids[0] ) > 0:
                        return qids[0]
                    else:
                        return qids[1]
                else:
                    return ''
                    
            else:
                return ''
    else:
        return ''
    


# There are cases in which the Library and Wikidata qids are of the same author
# but the name in Wikidata doesn't have articles
# The objective of this function, is to catch those cases
def get_wiki_id_from_name_without_articles(name, record):
    # Only make the search if there is any name
    if len(name ) > 0:
        author_name = name.replace(' ', '%20').replace(' de ', ' ').replace(' des ', ' ').replace(' da ', ' ').replace(' das ', ' ').replace(' do ', ' ').replace(' dos ', ' ').replace('"', '')

        author_name = urllib.parse.quote(author_name)
        languages = ['pt', 'en']
        qids = []
        
        if record % 5 == 0 : time.sleep(1)
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
            # print('Retrieved', len(data), 'characters', data[:20].replace('\n', ' '))

            js = json.loads(data) # converte os dados que estão numa string em json
            
            if len(js['results']['bindings']) > 0:
                
                id = js['results']['bindings'][0]['item']['value']

                pos = id.rindex('/')
                
                qid = id[pos + 1:].strip()
                
                if len(qid) > 0:
                    qids.append(qid)
                else:
                    qids.append('')
                
                # Check if there are two items in the list
                # If there is one, return that item
                # If there are two and they are equal, return one
                # If they are different, write on the error report     
                if len(qids) == 2:
                    if qids[0] != qids[1]:
                        f_wikidata_errors.write('The pt and en alias are different in record: ', record)
                        f_wikidata_errors.flush()
                    elif qids[0] == qids[1]:
                        return qids[0]

                elif len(qids) == 1:
                    if len(qids[0] ) > 0:
                        return qids[0]
                    else:
                        return qids[1]
                else:
                    return ''
                    
            else:
                return ''
    else:
        return ''

# get_wiki_id("Mario Soares", 11)