import sqlite3
import time
import ssl
import urllib.request, urllib.parse, urllib.error
from urllib.parse import urljoin
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta
import dates

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

global f_library_errors
f_library_errors = open(f'library_errors.txt', 'w')

def get_library_record_data(record):

    """
    """

    # Create a list to append the general data, to avoid returning a long list of variables    
    dict_some_fields = {}
    
            
    # Create a dictionnary to append the 200 data
    dict_200_field = {}
    name_200_field, surname_200_field, initials_200_field, dates_200_field, label = "", "", "", "", ""
    birth_date, death_date = 0, 0
    # Create a list to append the 400 fields data
    list_all_400_fields = []
    # field 400 is repeatable, so data is appended to lists
        
    baseurl = "https://urn.bnportugal.gov.pt/nca/unimarc/marcxchange?id="
    
    record_url = baseurl + str(record)

    try:
        xml = urllib.request.urlopen(record_url, context=ctx).read()

    # Taken from: https://stackoverflow.com/questions/53755173/urllib-exception-handling-in-python3
    except urllib.error.HTTPError as e:
        print("\n\nHTTP (library) Error : ", e)
        quit()
        # return {}, {}, []
    except urllib.error.URLError as e:
        print("URL (library) Error: ", e)
        # return {}, {}, []
        quit()
    

    try:            
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        print("Error when parsing xml: ", e)

    # Namespace
    # Got how it works from here: https://stackoverflow.com/questions/61551990/parse-xml-file-with-namespace-with-python
    namespace = {'unimarc': 'info:lc/xmlns/marcxchange-v2'}

    leader = root.findall('.//unimarc:leader', namespace)
    
    library_id, nationality, description = "", "", ""
    if len(leader) > 0:
        # Find out if the leader field has:
        # on position 5 the value "n" (new record) or "x" (corrected or revised)
        # From position 6 to 9 the value "x" for authority entry
        # On position 9 the value "a" (name of person entry)
        # Example: 01266cx a2200253 45         
        if re.findall('(nx|cx)+(\s{1,2}a)+', leader[0].text):
            
            controlfields = root.findall('.//unimarc:controlfield', namespace)

            # Get the controlfield 001 that has the Library Id
            if len(controlfields) > 0:
                
                for controlfield in controlfields:
                    tag = controlfield.get('tag')
                    if tag == '001':
                        library_id = controlfield.text

            # find the datafield elements
            # Asked ChatGPT about this
            datafields = root.findall('.//unimarc:datafield', namespace)
  
            for datafield in datafields:
                tag = datafield.get('tag')
                subfields = datafield.findall('unimarc:subfield', namespace)

                if tag == '102':
                    for subfield in subfields:
                        code = subfield.get('code')
                        value = subfield.text.strip()
                        if code == 'a':
                            nationality = value                             
                elif tag == '830':
                    for subfield in subfields:
                        code = subfield.get('code')
                        value = subfield.text.strip()
                        if code == '9':
                            nationality = value
                
                if tag == '200':
                    for subfield in subfields:
                        code = subfield.get('code')
                        # Some subfields may not have any data
                        try:
                            # Some names may end with a comma
                            # If that happens, remove it                            
                            value = subfield.text.replace(',', '')
                        except: 
                            f_library_errors.write(f'\nError in record: {record} - code {code}')
                            f_library_errors.flush()
                            continue
                        if code == 'a':
                            name_200_field = value.strip()
                        dict_200_field['name'] = name_200_field
                            
                        if code == 'b':
                            surname_200_field = value.strip()
                        dict_200_field['surname'] = surname_200_field
                                                    
                        if code == 'c':
                            initials_200_field = value.strip()
                        dict_200_field['initials'] = initials_200_field
                            
                        if code == 'f':
                            dates_200_field = value.strip()
                            # get the birth and deatg dates from the dates
                            birth_date, death_date = dates.get_dates(dates_200_field)
                        dict_200_field['dates'] = dates_200_field
                        dict_200_field['birth_date'] = birth_date
                        dict_200_field['death_date'] = death_date
                    label = surname_200_field.strip() + " " + name_200_field.strip()
                    dict_200_field['label'] = label.strip()
                            
                list_400_field = []
                dict_400_field = {}
                
                name_400_field, surname_400_field, initials_400_field, dates_400_field = "", "", "", ""
                alias = ""
                if tag == '400':
                    
                    for subfield in subfields:
                        
                        code = subfield.get('code')
                        # Some names may end with a comma
                        # If that happens, remove it

                        if subfield.text is not None:

                            if subfield.text.find(','):
                                value = subfield.text.replace(',', '')
                            else:
                                value = subfield.text
                                
                            if code == 'a':
                                name_400_field = value.strip()
                                dict_400_field['name'] = name_400_field
                                list_400_field.append(dict_400_field['name'])
                            if code == 'b':
                                surname_400_field = value.strip()
                                dict_400_field['surname'] = surname_400_field
                                list_400_field.append(dict_400_field['surname'])
                            if code == 'c':
                                initials_400_field = value.strip()
                                dict_400_field['initials'] = initials_400_field
                                list_400_field.append(dict_400_field['initials'])
                            if code == 'f':
                                dates_400_field = value.strip()
                                dict_400_field['dates'] = dates_400_field
                                list_400_field.append(dict_400_field['dates'])
                                
                            alias = surname_400_field + " " + name_400_field
                            dict_400_field['alias'] = alias.strip()
                            list_400_field.append(dict_400_field['alias'])

                    # Sometimes the 400 field names are the same as the 200 names
                    # To avoid that redundancy, those names are excluded
                    if label not in list_400_field:
                        list_all_400_fields.append(dict_400_field)

                if tag == '830':
                    for subfield in subfields:
                        code = subfield.get('code')
                        value = subfield.text
                        if code == 'a':
                            description = value



        # else:
        #     continue
    
    dict_some_fields['library_id'] = library_id
    dict_some_fields['nationality'] = nationality
    dict_some_fields['description'] = description

    
    # if record % 100 == 0 : time.sleep(1)
    

    return dict_some_fields, dict_200_field, list_all_400_fields
        
         