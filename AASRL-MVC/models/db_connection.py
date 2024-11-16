import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/jeiso/OneDrive/Code/AASRL/.flaskenv")

class Database:
    def __init__(self):
        self.config = {
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'host': os.getenv('MYSQL_HOST'),
            'port': os.getenv('MYSQL_PORT'),
            'database': os.getenv('MYSQL_DB'),
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True)
            print("Conexión exitosa a la base de datos.")
        except mysql.connector.Error as err:
            print(f"Error al conectar a la base de datos: {err}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Conexión cerrada.")

    def execute_query(self, query, params=None):
        try:
            self.connect()
            self.cursor.execute(query, params)
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"Error al ejecutar la consulta: {err}")
        finally:
            self.disconnect()

    def fetch_all(self, query, params=None):
        try:
            self.connect()
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(f"Error al obtener datos: {err}")
            return []
        finally:
            self.disconnect()
