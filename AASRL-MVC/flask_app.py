from flask import Flask,render_template, request
from .models.graphs import Graphs
from .models.server_model import ServerModel
from .models.execute_commands import ExecuteComm
from flask_login import LoginManager, login_user, logout_user, login_required

def Flaskapp():
    app = Flask(__name__)
    app_dash = Graphs()
    app_dash.create_dash(app)

    @app.route('/')
    def home():
        return ""#Crear el login
        
    @app.route('/Tasks')
    def Tasks():
        servers = ServerModel()
        host = servers.get_servers()
        return render_template('Tasks.html',host=host)

    @app.route('/Servers')
    def Servers():
        servers = ServerModel() 
        servers_info = servers.get_servers_info()
        servers_count = len(servers_info)
        return render_template('Servers.html',servers_info=servers_info,servers_count=servers_count)

    @app.route('/Dashboard')
    def Dashboard():
        servers = ServerModel()
        host = len(servers.get_servers())
        return render_template('Dashboard.html',host=host)
    
    @app.route('/Tasks/submit', methods=['POST'])
    def Submit():
        host = request.form['server_id']
        command = request.form['command']
        task = ExecuteComm()
        submit = task.execute_commands_remotely(host,command)
        if submit:
            return ''' <script> alert("Comando ejecutado exitosamente"); window.location.href = "/Tasks"; </script> '''
        else:
            return ''' <script> alert("No se ejecutó el comando"); window.location.href = "/Tasks"; </script> '''
    
    return app