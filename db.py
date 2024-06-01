# pylint: disable=global-at-module-level
import sqlite3

# Whenever the script is ran, the databas will be deleted and a new one is creted

DATABASE = 'Wikidata.sqlite'


def create_database():

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS Authors')

    cur.execute('''
                CREATE TABLE Authors (id INTEGER PRIMARY KEY AUTOINCREMENT, library_id TEXT, name TEXT, 
                surname TEXT, initials TEXT, wikidata_label_id TEXT, label TEXT, wikidata_alias_id, alias TEXT, dates TEXT, nationality TEXT, description TEXT)
                    ''')



def update_author(data_from_some_fields, data_from_200_field, data_from_400_fields, label_qid, wikidata_400_fields):
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
    # Had: and len(data_from_200_field['dates']) > 0, but I removed it
    if row is None and data_from_some_fields['nationality'] == 'PT':
        if len(data_from_400_fields) > 0:
            for i in range(len(data_from_400_fields)):
                cur.execute('''INSERT INTO Authors (library_id, name, surname, initials, wikidata_label_id, label, wikidata_alias_id, alias, dates, nationality, description)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (data_from_some_fields['library_id'], data_from_200_field['name'], data_from_200_field['surname'], data_from_200_field['initials'], label_qid, data_from_200_field['label'], '', '', data_from_200_field['dates'], 'Portugal', data_from_some_fields['description']))
            conn.commit()
        else: 
            for i in range(1):
                cur.execute('''INSERT INTO Authors (library_id, name, surname, initials, wikidata_label_id, label, wikidata_alias_id, alias, dates, nationality, description)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (data_from_some_fields['library_id'], data_from_200_field['name'], data_from_200_field['surname'], data_from_200_field['initials'], label_qid, data_from_200_field['label'], '', '', data_from_200_field['dates'], 'Portugal', data_from_some_fields['description']))
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
                count += 1
                first_row += 1
        