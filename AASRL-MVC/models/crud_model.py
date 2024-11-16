from .db_connection import Database

class CrudModel:
    def __init__(self):
        self.db = Database()

    def create(self, query, params):
        self.db.execute_query(query, params)

    def read(self, query, params=None):
        return self.db.fetch_all(query, params)

    def update(self, query, params):
        self.db.execute_query(query, params)

    def delete(self, query, params):
        self.db.execute_query(query, params)
