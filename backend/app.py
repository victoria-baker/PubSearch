import json
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
from cosinesim import search as cosine_search
from jaccardsim import search as jaccard_search
from jaccardsim import getTop5 as return_top5
from jaccardsim import rocchio

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ["ROOT_PATH"] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, "init.json")

# Assuming your JSON data is stored in a file named 'init.json'
with open(json_file_path, "r") as file:
    data = json.load(file)
    episodes_df = pd.DataFrame(data["episodes"])
    reviews_df = pd.DataFrame(data["reviews"])

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return render_template("index.html", title="sample html")


@app.route("/send-data", methods=["POST"])
def receive_data():
    data = request.get_json()
    search_query = data["search_term"]
    sy = data["sy"]
    ey = data["ey"]
    author = data["author"]
    results = return_top5(search_query, sy, ey, author)
    # Format results as needed before sending back to the client
    return results


@app.route("/send-lists", methods=["POST"])
def receive_data_lists():
    data = request.get_json()
    search_term = data["search_term"]
    rel_list = data["rel_list"]
    irrel_list = data["irrel_list"]
    sy = data["sy"]
    ey = data["ey"]
    author = data["author"]
    results = rocchio(search_term, rel_list, irrel_list, sy, ey, author)
    print("RESULTS", results)
    return results


if "DB_NAME" not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5000)
