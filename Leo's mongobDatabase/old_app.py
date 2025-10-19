from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

app = Flask(__name__)

# read MongoDB information from .env file
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
DB_NAME = os.getenv("DB_NAME", "todolist_db")

# connect to database
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

@app.route('/')
def home():
    return jsonify({"message": "To-Do List MongoDB connected successfully!"})

# initialize sample data
@app.route('/init')
def init_data():
    db.tasks.delete_many({})  # clear old tasks

    db.tasks.insert_many([
        {
            "title": "cooking",
            "tag": "fod",
            "description": "cook something good",
            "duration": "45min",
            "creator": "Leo"
        },
        {
            "title": "study",
            "tag": "study",
            "description": "Finish database",
            "duration": "2h",
            "creator": "Leo"
        },
        {
            "title": "work out",
            "tag": "health",
            "description": "50 push-ups",
            "duration": "1h",
            "creator": "Leo"
        }
    ])

    return jsonify({"message": "Sample To-Do tasks inserted!"})

# get all tasks
@app.route('/get_tasks')
def get_tasks():
    tasks = list(db.tasks.find({}, {"_id": 0}))
    return jsonify(tasks)

# filter tasks by tag
@app.route('/get_tasks/<tag>')
def get_tasks_by_tag(tag):
    tasks = list(db.tasks.find({"tag": tag}, {"_id": 0}))
    if not tasks:
        return jsonify({"message": f"No tasks found for tag '{tag}'"})
    return jsonify(tasks)

# clear tasks
@app.route('/clear')
def clear_tasks():
    db.tasks.delete_many({})
    return jsonify({"message": "All tasks cleared!"})

if __name__ == '__main__':
    app.run(debug=True)
