from flask import Flask
from mongoengine import connect

# Initialize the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
connect(host=app.config["DATABASE_URI"])

from app import views
