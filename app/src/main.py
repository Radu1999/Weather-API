from flask import Flask, request
from countries import countries_app
from cities import cities_app
from temperatures import temperatures_app

app = Flask(__name__)
app.register_blueprint(countries_app)
app.register_blueprint(cities_app)
app.register_blueprint(temperatures_app)

if __name__ == '__main__':
   app.run()