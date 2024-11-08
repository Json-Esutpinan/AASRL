import paramiko

# Credenciales servidor
hostname = '192.168.1.57'
port = 22
username = '**************'
password = '**************'

# Cliente SSH
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname, port, username, password)
    stdin, stdout, stderr = client.exec_command('sudo systemctl start mysql')
    output = stdout.read().decode()
    print(output)
    errors = stderr.read().decode()
    if errors:
        print(errors)
finally:
    client.close()