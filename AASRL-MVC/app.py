from flask import Flask,render_template
from flask_login import LoginManager, login_user, logout_user, login_required

app = Flask(__name__)

@app.route('/')
def home():
    return "Pinged your deployment. You successfully connected to MongoDB!"
    
@app.route('/Tasks')
def Tasks():
    return render_template('Tasks.html')

@app.route('/Servers')
def Servers():
    return render_template('Servers.html')

@app.route('/Dashboard')
def Dashboard():
    return render_template('Dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)