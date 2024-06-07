"""
The objective of this program is to extract the author's data (personal names) from the Portuguese National Library authorities database
and write it in Wikidata (https://www.wikidata.org/) using the OpenRefine software.
The database has data of the author's that contributed to the works available at the library.
The authorities data is in the UNIMARC format (https://www.ifla.org/wp-content/uploads/2019/05/assets/uca/unimarc-authorities-format.pdf)
Wikidata data format: https://www.wikidata.org/wiki/Help:About_data 

Although OpenRefine detects if the database author data already exists in Wikidata before exporting it,
a check is made, so that the new entries can be distinguished and grouped apart from already existent ones

The database data is available in several formats, but the one used in the app to retrieve the author's data is the MarcXchange format, 
a XML-based exchange format (https://www.loc.gov/standards/iso25577/marcxchange-2-0.xsd)

Example:
<collection xmlns="info:lc/xmlns/marcxchange-v2">
<record format="Unimarc" type="authority">
<leader>00547cx a2200169 45 </leader>
<controlfield tag="001">320</controlfield>
...
<datafield ind1=" " ind2="1" tag="200">
<subfield code="a">Abecasis,</subfield>
<subfield code="b">Fernando Manzanares,</subfield>
<subfield code="f">1922-</subfield>
</datafield>
...
<datafield ind1=" " ind2="1" tag="400">
<subfield code="a">Abecasis,</subfield>
<subfield code="b">Fernando Maria</subfield>
</datafield>
<datafield ind1=" " ind2="1" tag="400">
<subfield code="a">Abecasis,</subfield>
<subfield code="b">Fernando Maria Alberto do Perpétuo Socorro Manzanares</subfield>
</datafield>
...
<datafield ind1=" " ind2=" " tag="830">
<subfield code="a">Engenheiro, Investigador</subfield>
</datafield>
...

The database has other types of authors data besides personal names, such as: corporations, family names, places, etc.,
but only the authors (personal names) data is to be exported
The records of the intended type have the following codes in the leader field:
    - "n" (new) or "c" (corrected") codes in position 5
    - "x" (new authority) code in position 6
    - "a" (name of person) code in position 9

The database data fields that can be exported to Wikidata, are:
- Label
The database "200" field data can be exported to the Wikidata "Label" field, which is where the name of the author is registered
The "200" field is non repeatable. The subfields that can be concatenated and used to form the Label are: 
code "$b" - Part of name other than entry element (surname) and code "$a" - Entry element (name)

- Alias
The "Alias" Wikidata field can be comprised of the library database "400" subfields data
The field is repeatable, which means that that may exist multiple "400" fields
The subfields code data to be concatenated are also $b and $a 

- Description
The "830" field data can be exported to the "Description" Wikidata field

- Date of birth and date of death
The author's birth and death dates are registered in subfield "$f" of the "200" field, with an hifen separating them (ex.: 1922-2001)
Since the Wikidata birth and death dates are filled in separate fields, the database dates have to be isolated
There are also several cases where the dates don't have four digits. Those cases have to be identified and mapped to the Wikidata dates format
The Wikidata birth date is registered in property "P19" and the death date in "P20"

Occupations
It is possible to obtain the author's occupations and professions from the description data (field "830")
The description words are searched in Wikidata and exported if they exist and are either a occupation or a profession

To export the data with OpenRefine, if an author has for instance 3 alias, the data should have the following format:
label                           alias                                                           dates   description            
Fernando Manzanares Abecasis	Fernando Abecasis	                                            1922-	Engenheiro, Investigador
Fernando Manzanares Abecasis	Fernando Maria Abecasis	                                        1922-	Engenheiro, Investigador
Fernando Manzanares Abecasis	Fernando Maria Alberto do Perpétuo Socorro Manzanares Abecasis	1922-	Engenheiro, Investigador

"""   

import sqlite3
import time
import ssl
import urllib.request, urllib.parse, urllib.error
from urllib.parse import urljoin
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta
import db
from library import get_library_record_data
import wikidata

while True:
    new_database = input('Create a new database? (y/n) ')
    if len(new_database) < 1:
        continue
    if new_database.lower() == "y":
        db.create_database()
        break
    else:
        break


while True:
    frecord = input('Enter first record to scrape: ')
    # To remove any non number characters
    frecord = re.findall('[0-9]+', frecord)
    frecord = "".join(frecord)
    if len(frecord) < 1:
        continue

    first_record = int(frecord.strip())

    lrecord = input('Enter last record to scrape: ')
    lrecord = re.findall('[0-9]+', lrecord)
    lrecord = "".join(lrecord)
    if len(lrecord) < 1:
        continue

    last_record = int(lrecord.strip())
    break
    # baseurl = "https://urn.bnportugal.gov.pt/nca/unimarc/marcxchange?id="

for record in range(first_record, last_record, 1):
    label_qid = ""
    
    alias_qid_with_articles, alias_qid_without_articles = [], []
    print("\nID: ", record)
    # if record % 500 == 0:
    #     time.sleep(3)
    data_from_some_fields, data_from_200_field, data_from_400_fields = get_library_record_data(record)

    # Verify if the author already exists
    # Only write the ones that still don't exist in the database
    # And whose data has dates and with portuguese nationality
    
   
    # For the time being, get and write data only of portuguese authors with death dates from 1900 to 1940   
    if 'label' in data_from_200_field and data_from_some_fields['nationality'] == 'PT' and (data_from_200_field['death_date'] > 1899 and data_from_200_field['death_date'] < 1941):  
        wikidata_400_fields = []        
    
        if len(data_from_200_field['label']) > 0:
            time.sleep(0.5)
            label_qid_with_articles = wikidata.get_wikidata_id(data_from_200_field['label'], record)
            # There are cases in which the library label has articles and Wikidata doesn't
            time.sleep(0.5)
            label_qid_without_articles = wikidata.get_wikidata_id_from_name_without_articles(data_from_200_field['label'], record)
            if len(label_qid_with_articles) > 0:
                label_qid = label_qid_with_articles
            else:
                label_qid = label_qid_without_articles
        
        if len(data_from_400_fields) > 0:
            for i in range(len(data_from_400_fields)):
                if len(data_from_400_fields[i]['alias']) > 0:
                    time.sleep(0.5)
                    alias_qid_with_articles = wikidata.get_wikidata_id(data_from_400_fields[i]['alias'], record)
                    time.sleep(0.5)
                    alias_qid_without_articles = wikidata.get_wikidata_id_from_name_without_articles(data_from_400_fields[i]['alias'], record)

                if len(alias_qid_with_articles) > 0:
                    wikidata_400_fields.append(alias_qid_with_articles)
                elif len(alias_qid_without_articles) > 0:
                    wikidata_400_fields.append(alias_qid_without_articles)
                else:
                    wikidata_400_fields.append('')
                        
        print(f'\n200 field: {data_from_200_field} - 400 fields: {data_from_400_fields}')    
        print(f'Wikidata label QID: {label_qid} - Alias QIDs: {wikidata_400_fields}')

        if len(data_from_200_field) > 0:        
                db.update_author(data_from_some_fields, data_from_200_field, data_from_400_fields, label_qid, wikidata_400_fields)
            

