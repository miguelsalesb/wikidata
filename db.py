"""
In the library authority record:
The author name for which he/she is best known, is registered on field 200
The name of the author is registered in subfield $a and the surname in subfield $b

The author other names (his/her heteronyms, for example), are registered on the 400 field

These are the fields that are extracted from the authority record and written in the database

library_id							001
name								200$a
surname								200$b
initials							200$c
label								200$b + " " + 200$a
alias								400$b + " " + 400$a (the 400 field is repeatable, so there may be several alias)
dates								200$f
nationality							102$a or 830$9
description							830$a

The library data will be stored in the variables:
library_id							data_from_some_fields['library_id']
name								data_from_200_field['name']
surname								data_from_200_field['surname']
initials							data_from_200_field['initials']
label								data_from_200_field['label']
alias								data_from_400_fields['alias']
dates								data_from_200_field['dates']
nationality							data_from_some_fields['nationality']
description							data_from_some_fields['description']


The name of the author is searched on Wikidata to get his/her Wikidata ID (QID) through the Wikidata Query Service (https://query.wikidata.org/)
And then the resultant QID is searched in order to extract the data that allows:
- to confirm if the author already exists or not in Wikidata
- to perceive which library data still doesn't exist in the author's Wikidata page

The Wikidata data will be stored in the variables:
wikidata_label_id					wikidata_label_qid
wikidata_author_library_id_200		wikidata_author_data_200['wikidata_author_library_id']
wikidata_author_library_id_400		wikidata_author_data_400['wikidata_author_library_id']
wikidata_alias_id					wikidata_alias_qids[]
wikidata_author_birth_date_200		wikidata_author_data_200['wikidata_author_birth_date']
wikidata_author_death_date_200		wikidata_author_data_400['wikidata_author_death_date']
wikidata_author_birth_date_400		wikidata_author_data_400['wikidata_author_birth_date']
wikidata_author_death_date_400		wikidata_author_data_200['wikidata_author_death_date']
wikidata_author_description_200		wikidata_author_data_200['wikidata_author_description']
wikidata_author_description_400		wikidata_author_data_400['wikidata_author_description']
wikidata_author_occupations_200		wikidata_author_data_200['wikidata_author_occupations']
wikidata_author_occupations_400		wikidata_author_data_400['wikidata_author_occupations']
wikidata_author_notable_work_200	wikidata_author_data_200['wikidata_author_notable_work']
wikidata_author_notable_work_400	wikidata_author_data_400['wikidata_author_notable_work']


"""
import sqlite3

# Whenever the script is ran, the databas will be deleted and a new one is creted

DATABASE = 'Wikidata_teste2.sqlite'


def create_database():

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS Authors')

    cur.execute('''
                CREATE TABLE Authors (id INTEGER PRIMARY KEY AUTOINCREMENT, library_id	TEXT, wikidata_label_id TEXT, wikidata_author_library_id_200 TEXT, 
                wikidata_author_library_id_400 TEXT, name TEXT, surname TEXT, initials TEXT, label TEXT, wikidata_alias_id TEXT, alias TEXT, dates TEXT, 
                wikidata_author_birth_date_200 TEXT, wikidata_author_death_date_200 TEXT, wikidata_author_birth_date_400 TEXT, wikidata_author_death_date_400 TEXT, 
                nationality TEXT, description TEXT, wikidata_author_description_200 TEXT, wikidata_author_description_400 TEXT, wikidata_author_occupations_200 TEXT, 
                wikidata_author_occupations_400 TEXT, wikidata_author_notable_work_200 TEXT, wikidata_author_notable_work_400 TEXT)
                    ''')

def update_author(data_from_some_fields, data_from_200_field, data_from_400_fields, wikidata_label_qid, wikidata_400_fields, wikidata_author_data_200, wikidata_author_data_400):
    """
    """
    # If some another first and end numbers of records to be scrapped are defined, the new data will be added
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Verify if the author already exists
    # Only write the ones that still don't exist in the database
    # And whose data has dates and with portuguese nationality
    cur.execute('SELECT name, surname FROM Authors WHERE name = ? and surname = ?  ', (data_from_200_field['name'], data_from_200_field['surname']))
    row = cur.fetchone()
    
    occupations = ""
    notable_work = ""
    # Had: and len(data_from_200_field['dates']) > 0, but I removed it
    if row is None and data_from_some_fields['nationality'] == 'PT':
        if len(data_from_400_fields) > 0 and wikidata_author_data_200 is not None:
            # In order for the data to have the format which is exportable by OpenRefine, the 200 field data has to be repeated as many times as
            # the number of 400's fields
            for _ in range(len(data_from_400_fields)):
                cur.execute('''INSERT INTO Authors (library_id, wikidata_label_id, wikidata_author_library_id_200, wikidata_author_library_id_400, name, surname, initials, label, wikidata_alias_id, alias, dates, wikidata_author_birth_date_200, wikidata_author_death_date_200, wikidata_author_birth_date_400, wikidata_author_death_date_400, nationality, description, wikidata_author_description_200, wikidata_author_description_400, wikidata_author_occupations_200, wikidata_author_occupations_400, wikidata_author_notable_work_200, wikidata_author_notable_work_400)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (data_from_some_fields['library_id'], wikidata_label_qid, wikidata_author_data_200['wikidata_author_library_id'], '', data_from_200_field['name'], data_from_200_field['surname'], data_from_200_field['initials'], data_from_200_field['label'], '', '', data_from_200_field['dates'], wikidata_author_data_200['wikidata_author_birth_date'], '', '', wikidata_author_data_200['wikidata_author_death_date'], 'Portugal', data_from_some_fields['description'], wikidata_author_data_200['wikidata_author_description'], '', ",".join(wikidata_author_data_200['wikidata_author_occupations']), '', ",".join(wikidata_author_data_200['wikidata_author_notable_work']), ''))
        elif len(data_from_400_fields) == 0 and wikidata_author_data_200 is not None: 
            for _ in range(1):
                cur.execute('''INSERT INTO Authors (library_id, wikidata_label_id, wikidata_author_library_id_200, wikidata_author_library_id_400, name, surname, initials, label, wikidata_alias_id, alias, dates, wikidata_author_birth_date_200, wikidata_author_death_date_200, wikidata_author_birth_date_400, wikidata_author_death_date_400, nationality, description, wikidata_author_description_200, wikidata_author_description_400, wikidata_author_occupations_200, wikidata_author_occupations_400, wikidata_author_notable_work_200, wikidata_author_notable_work_400)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (data_from_some_fields['library_id'], wikidata_label_qid, wikidata_author_data_200['wikidata_author_library_id'], '', data_from_200_field['name'], data_from_200_field['surname'], data_from_200_field['initials'], data_from_200_field['label'], '', '', data_from_200_field['dates'], wikidata_author_data_200['wikidata_author_birth_date'], '', '', wikidata_author_data_200['wikidata_author_death_date'], 'Portugal', data_from_some_fields['description'], wikidata_author_data_200['wikidata_author_description'], '', ",".join(wikidata_author_data_200['wikidata_author_occupations']), '', ",".join(wikidata_author_data_200['wikidata_author_notable_work']), ''))
        conn.commit()
        # Get the last row written in the table
        # The first alias (400 field data) should be written in the same row as the label (name of the author from the 200 field)
        # A calculation is made to get the exact row where that data should be writtem
        cur.execute('SELECT id FROM Authors ORDER BY id DESC LIMIT 1')
        row = cur.fetchone()
        if row is not None:
            count = 1
            first_row = int(row[0] - len(data_from_400_fields)) + 1

            while count <= len(data_from_400_fields):
                
                cur.execute('''UPDATE Authors SET alias = ?, wikidata_alias_id = ? WHERE id = ?
                            ''', (data_from_400_fields[count-1]['alias'], wikidata_400_fields[count-1], first_row))
                conn.commit()
                
                occupations = ",".join(wikidata_author_data_400[count-1]['wikidata_author_occupations'])
                notable_work = ",".join(wikidata_author_data_400[count-1]['wikidata_author_notable_work'])
                cur.execute('''UPDATE Authors SET wikidata_author_library_id_400 = ?, wikidata_author_death_date_400 = ?, wikidata_author_birth_date_400 = ?, wikidata_author_description_400 = ?, wikidata_author_occupations_400 = ?, wikidata_author_notable_work_400 = ? WHERE id = ?
                            ''', (wikidata_author_data_400[count-1]['wikidata_author_library_id'], wikidata_author_data_400[count-1]['wikidata_author_death_date'], wikidata_author_data_400[count-1]['wikidata_author_birth_date'], wikidata_author_data_400[count-1]['wikidata_author_description'], occupations, notable_work, first_row))
                conn.commit()
                count += 1
                first_row += 1
        