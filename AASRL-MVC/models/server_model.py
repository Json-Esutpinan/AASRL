from .crud_model import CrudModel
from .encrypt import Encrypt

class ServerModel(CrudModel):
    
    def __init__(self):
        super().__init__()

    def create_server(self,data):
        encrypt = Encrypt()
        host, credentials, username = data
        salt = encrypt.generate_salt()
        hashed_password = encrypt.hash_password(credentials, salt)
        query = "INSERT INTO server_info (host, credentials,username,salt) VALUES (%s, %s,%s,%s)"
        self.create(query, (host,hashed_password,username,salt))

    def get_servers(self):
        query = "SELECT host FROM server_info"
        return self.read(query)

    def get_servers_byId(self,host):
        query = "SELECT host,port,username,credentials FROM server_info WHERE host = %s"
        return self.read(query,host)
    
    def delete_server(self, host):
        query = "DELETE FROM server_info WHERE host = %s"
        self.delete(query,host)
        
    def insert_server_info(self,data):
        query = "INSERT INTO so_info (cpu,memory,disk,so_desc,id_server) VALUES (%s, %s,%s,%s,s, (SELECT id FROM server_info WHERE host = %s))"
        self.read(query,data)
        
    def get_servers_info(self):
        query = "SELECT cpu,memory,disk,so_desc FROM so_info"
        return self.read(query)