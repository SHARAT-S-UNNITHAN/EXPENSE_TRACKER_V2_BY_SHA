import sqlite3

def get_all_table_details(database_file):
    
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"Tables in database '{database_file}':")
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        
        
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print("Columns:")
        for column in columns:
            col_id = column[0]         
            col_name = column[1]       
            col_type = column[2]        
            not_null = bool(column[3])  
            default_value = column[4]   
            primary_key = bool(column[5])  

            print(f"  - Column ID: {col_id}")
            print(f"    Name: {col_name}")
            print(f"    Type: {col_type}")
            print(f"    Not NULL: {not_null}")
            print(f"    Default Value: {default_value}")
            print(f"    Primary Key: {primary_key}")
    
    
    conn.close()


get_all_table_details("mydatabase")
