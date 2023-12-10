import sqlite3
from datetime import datetime

class DataHandler:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def add_data(self, table_name, data):
        insert_query = f"INSERT INTO {table_name} VALUES ({','.join(['?'] * len(data))})"
        self.cursor.execute(insert_query, data)
        self.conn.commit()

    def get_data_by_date(self, table_name, date_column, target_date):
        select_query = f"SELECT * FROM {table_name} WHERE {date_column} = ?"
        self.cursor.execute(select_query, (target_date,))
        return self.cursor.fetchall()

    def delete_data_by_id(self, table_name, id_column, target_id):
        delete_query = f"DELETE FROM {table_name} WHERE {id_column} = ?"
        self.cursor.execute(delete_query, (target_id,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()