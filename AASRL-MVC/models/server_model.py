from models.crud_model import CrudModel
from models.encrypt import generate_salt,hash_password,verify_password
from hashlib import sha256

class ServerModel(CrudModel):
    def __init__(self):
        super().__init__()

    def hash_password(self, password):
        return sha256(password.encode()).hexdigest()

    def create_server(self, user_data):
        host, credentials, username = user_data
        salt = generate_salt()
        hashed_password = hash_password(credentials, salt)
        query = "INSERT INTO so_info (host, credentials,username,salt) VALUES (%s, %s,%s,%s)"
        self.create(query, (host,hashed_password,username,salt))

    def get_servers(self):
        query = "SELECT host FROM so_info"
        return self.read(query)

    def get_servers_byId(self,id):
        query = "SELECT * FROM so_info WHERE host = %s"
        return self.read(query,id)
    
    def delete_user(self, host):
        query = "DELETE FROM so_info WHERE host = %s"
        self.delete(query,host)