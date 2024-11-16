import paramiko
from .server_model import ServerModel

class ExecuteComm:
    
    def __init__(self):
        pass
    
    def read_commands(self,file_path):
        with open(file_path, "r") as file:
            commands = file.readlines()
        return [command.strip() for command in commands]

    def execute_commands_remotely(self,host, commands):
        server = ServerModel()
        result = server.get_servers_byId(host)
        
        if result:
            server_info= result[0]
            info = {
                'host': server_info['host'],
                'port': server_info['port'],
                'username': server_info['username'],
                'credentials': server_info['credentials']
            }
            try:
                list_result = []
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                ssh.connect(info["host"], info["port"], info["username"], info["credentials"])
                
                for command in commands:
                    stdin, stdout, stderr = ssh.exec_command(command)
                    list_result.append(stdout.read().decode())
                ssh.close()
                return True
            except Exception as e:
                return False
        else:
            return False