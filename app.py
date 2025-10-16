from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()  

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["TaskDB"]
tasks = db["tasks"]

@app.route("/")
def home():
    return render_template("test.html")

@app.route("/tasks")
def task_list():
    all_tasks = list(tasks.find())
    return render_template("tasks.html", tasks=all_tasks)

@app.route("/tasks/<id>")
def task_detail(id):
    task = tasks.find_one({"_id": ObjectId(id)})
    return render_template("task_detail.html", task=task)

@app.route("/tasks/new", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        tags = request.form["tags"]
        due_date = request.form["due_date"]
        completed = "completed" in request.form
        tasks.insert_one({
            "title": title,
            "description": description,
            "tags": tags,
            "due_date": due_date,
            "completed": completed
        })
        return redirect(url_for("task_list"))
    return render_template("add_task.html")

@app.route("/tasks/<id>/edit", methods=["GET", "POST"])
def edit_task(id):
    task = tasks.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
        updated_task = {
            "title": request.form["title"],
            "description": request.form["description"],
            "tags": request.form["tags"],
            "due_date": request.form["due_date"],
            "completed": "completed" in request.form
        }
        tasks.update_one({"_id": ObjectId(id)}, {"$set": updated_task})
        return redirect(url_for("task_detail", id=id))
    return render_template("edit_task.html", task=task)

@app.route("/tasks/search")
def search_tasks():
    keyword = request.args.get("q", "")
    results = list(tasks.find({"title": {"$regex": keyword, "$options": "i"}}))
    return render_template("search.html", tasks=results, keyword=keyword)

@app.route("/tasks/completed")
def completed_tasks():
    completed = list(tasks.find({"completed": True}))
    return render_template("completed.html", tasks=completed)

@app.route("/tasks/<id>/delete")
def delete_task(id):
    tasks.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("task_list"))

if __name__ == "__main__":
    app.run(debug=True)
