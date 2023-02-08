from flask import Flask
import json

# Create Flask application
app = Flask(__name__)

app.config.from_file("../.env.json", load=json.load)

from backend import routes