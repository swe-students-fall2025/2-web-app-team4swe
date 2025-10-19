from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient, ASCENDING
from bson import ObjectId
from dotenv import load_dotenv
from datetime import date
import os, re

load_dotenv()

app = Flask(__name__, template_folder="html_templates")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# ----- Mongo -----
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
MONGO_DB  = os.getenv("MONGO_DB",  "weekly_planner")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
tasks_col = db.tasks
users_col = db.users

tasks_col.create_index([("deleted", ASCENDING)])
tasks_col.create_index([("due_date", ASCENDING)])
tasks_col.create_index([("tag", ASCENDING)])
users_col.create_index("email", unique=True)

# ----- Login manager -----
login_manager = LoginManager(app)
login_manager.login_view = "login" 

class MongoUser(UserMixin):
    def __init__(self, doc):
        self.id = str(doc["_id"])
        self.email = doc.get("email")
        self.name = doc.get("name") or self.email.split("@")[0]

@login_manager.user_loader
def load_user(user_id: str):
    try:
        doc = users_col.find_one({"_id": ObjectId(user_id)})
        return MongoUser(doc) if doc else None
    except Exception:
        return None

# ----- helpers -----
def today_str():
    return date.today().isoformat()

def q_active_by_user():
    return {"deleted": {"$ne": True}, "user_id": ObjectId(current_user.id)}

def with_str_id(d):
    d = dict(d)
    d["_id"] = str(d["_id"])
    return d

def calc_stats():
    tdy = today_str()
    base = {"user_id": ObjectId(current_user.id)}
    total = tasks_col.count_documents({**base, "deleted": {"$ne": True}})
    upcoming = tasks_col.count_documents({**base, "deleted": {"$ne": True}, "due_date": {"$gt": tdy}})
    today_cnt = tasks_col.count_documents({**base, "deleted": {"$ne": True}, "due_date": tdy})
    tags_cnt = len([t for t in tasks_col.distinct("tag", {**base, "deleted": {"$ne": True}}) if t])
    return {"total": total, "upcoming": upcoming, "today": today_cnt, "tags": tags_cnt}

@app.context_processor
def inject_globals():
    return {"app_name": "Efficient Max"}

#         Auth
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name  = request.form.get("name","").strip()
        email = (request.form.get("email","") or "").strip().lower()
        pwd   = request.form.get("password","")
        if not email or not pwd:
            flash("Email and password are required.")
            return redirect(url_for("register"))
        if users_col.find_one({"email": email}):
            flash("Email already registered.")
            return redirect(url_for("register"))
        users_col.insert_one({
            "name": name, "email": email,
            "password_hash": generate_password_hash(pwd),
            "created_at": today_str()
        })
        flash("Account created. Please sign in.")
        return redirect(url_for("login"))
    return render_template("login.html", title="Register", mode="register")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email","") or "").strip().lower()
        pwd   = request.form.get("password","")
        user  = users_col.find_one({"email": email})
        if not user or not check_password_hash(user["password_hash"], pwd):
            flash("Invalid email or password.")
            return redirect(url_for("login"))
        login_user(MongoUser(user), remember=True)
        return redirect(url_for("home"))
    return render_template("login.html", title="Sign In", mode="login")

@app.route("/logout", methods=["POST","GET"])
@login_required
def logout():
    logout_user()
    flash("Signed out.")
    return redirect(url_for("login"))

#  Pages
@app.route("/", endpoint="home")
@login_required
def home():
    user = current_user.id
    tdy = date.today().isoformat()

    total = tasks_col.count_documents(q_active_by_user())
    upcoming = tasks_col.count_documents({**q_active_by_user(), "due_date": {"$gt": tdy}})
    today = tasks_col.count_documents({**q_active_by_user(), "due_date": tdy})
    tags = len(tasks_col.distinct("tag", q_active_by_user()))
    overdue = tasks_col.count_documents({**q_active_by_user(), "due_date": {"$lt": tdy}})

    stats = {
        "total": total,
        "upcoming": upcoming,
        "today": today,
        "tags": tags,
        "overdue": overdue, 
    }

    return render_template("home.html", stats=stats)

# tasks list ( priority order )
@app.route("/tasks", endpoint="tasks")
@login_required
def tasks():
    filt = request.args.get("filter", "all")
    tag  = request.args.get("tag")

    q = q_active_by_user()
    if filt == "upcoming":
        q["due_date"] = {"$gt": today_str()}
    elif filt == "today":
        q["due_date"] = today_str()
    elif filt == "tag" and tag:
        q["tag"] = tag

    items = [with_str_id(t) for t in tasks_col.find(q).sort("due_date", ASCENDING)]
    return render_template("tasks.html", title="Task List", tasks=items, active=filt)

# add tasks
@app.route("/task/new", methods=["GET","POST"], endpoint="tasks_new")
@login_required
def tasks_new():
    if request.method == "POST":
        doc = {
            "creator": current_user.name,
            "title": request.form.get("title","").strip(),
            "description": request.form.get("description","").strip(),
            "due_date": request.form.get("due_date","").strip(),
            "tag": request.form.get("tag","").strip(),
            "deleted": False,
            "user_id": ObjectId(current_user.id),
        }
        tasks_col.insert_one(doc)
        flash("Task created.")
        return redirect(url_for("tasks", filter="all"))

    existing = sorted([t for t in tasks_col.distinct("tag", q_active_by_user()) if t])
    return render_template("task_form.html",
                           title="Add Task", mode="new",
                           action=url_for("tasks_new"),
                           task=None, existing_tags=existing)

@app.route("/task/<task_id>", endpoint="task_detail")
@login_required
def task_detail(task_id):
    doc = tasks_col.find_one({"_id": ObjectId(task_id), **q_active_by_user()})
    if not doc:
        flash("Task not found.")
        return redirect(url_for("tasks", filter="all"))
    return render_template("task_detail.html", title="Task Details", task=with_str_id(doc))

@app.route("/task/<task_id>/edit", methods=["GET","POST"], endpoint="tasks_edit")
@login_required
def tasks_edit(task_id):
    doc = tasks_col.find_one({"_id": ObjectId(task_id), **q_active_by_user()})
    if not doc:
        flash("Task not found.")
        return redirect(url_for("tasks", filter="all"))

    if request.method == "POST":
        upd = {
            "title": request.form.get("title","").strip(),
            "description": request.form.get("description","").strip(),
            "due_date": request.form.get("due_date","").strip(),
            "tag": request.form.get("tag","").strip(),
        }
        tasks_col.update_one({"_id": doc["_id"]}, {"$set": upd})
        flash("Task updated.")
        return redirect(url_for("task_detail", task_id=task_id))

    existing = sorted([t for t in tasks_col.distinct("tag", q_active_by_user()) if t])
    return render_template("task_form.html",
                           title="Edit Task", mode="edit",
                           action=url_for("tasks_edit", task_id=task_id),
                           task=with_str_id(doc), existing_tags=existing)

# double check delete
@app.route("/task/<task_id>/soft-delete", methods=["POST"], endpoint="tasks_soft_delete")
@login_required
def tasks_soft_delete(task_id):
    tasks_col.update_one({"_id": ObjectId(task_id), "user_id": ObjectId(current_user.id)}, {"$set": {"deleted": True}})
    flash("Task moved to Trash.")
    return redirect(url_for("tasks", filter="all"))

# Trash
@app.route("/trash", endpoint="trash")
@login_required
def trash():
    items = [with_str_id(t) for t in tasks_col.find({"deleted": True, "user_id": ObjectId(current_user.id)}).sort("due_date", ASCENDING)]
    return render_template("trash.html", title="Trash", items=items)

@app.route("/task/<task_id>/restore", methods=["POST"], endpoint="tasks_restore")
@login_required
def tasks_restore(task_id):
    tasks_col.update_one({"_id": ObjectId(task_id), "user_id": ObjectId(current_user.id)}, {"$set": {"deleted": False}})
    flash("Task restored.")
    return redirect(url_for("trash"))

@app.route("/task/<task_id>/delete-permanent", methods=["POST"], endpoint="tasks_delete_permanent")
@login_required
def tasks_delete_permanent(task_id):
    tasks_col.delete_one({"_id": ObjectId(task_id), "user_id": ObjectId(current_user.id)})
    flash("Task deleted permanently.")
    return redirect(url_for("trash"))

# Tags list
@app.route("/tags", endpoint="tags")
@login_required
def tags():
    tags = sorted([t for t in tasks_col.distinct("tag", q_active_by_user()) if t])
    return render_template("tags.html", title="Tags", tags=tags)

# search
@app.route("/search", endpoint="search")
@login_required
def search():
    q_text = (request.args.get("q","") or "").strip()
    q_tag  = (request.args.get("tag","") or "").strip()
    searched = ("q" in request.args) or ("tag" in request.args)

    query = q_active_by_user()
    if q_text:
        query["$or"] = [
            {"title": {"$regex": re.escape(q_text), "$options": "i"}},
            {"description": {"$regex": re.escape(q_text), "$options": "i"}},
        ]
    if q_tag:
        query["tag"] = q_tag

    results = []
    if searched:
        results = [with_str_id(t) for t in tasks_col.find(query).sort("due_date", ASCENDING)]

    return render_template("search.html", title="Search", results=results, searched=searched)

# Overdue
@app.route("/overdue", endpoint="overdue")
@login_required
def overdue():
    tdy = today_str()
    items = []
    for t in tasks_col.find({**q_active_by_user(), "due_date": {"$lt": tdy}}).sort("due_date", ASCENDING):
        try:
            days = (date.fromisoformat(tdy) - date.fromisoformat(t["due_date"])).days
        except Exception:
            days = "-"
        d = with_str_id(t)
        d["days_overdue"] = days
        items.append(d)
    return render_template("overdue.html", title="Overdue", tasks=items)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

