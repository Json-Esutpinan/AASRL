from .flask_app import Flaskapp

app = Flaskapp()

if __name__ == '__main__':
    app.run(debug=True)