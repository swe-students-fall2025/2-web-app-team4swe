# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

A lightweight and custom mission web for users to save, search and organize their tasks on the internet.

## User stories

As a student, I want to organize my assignments into categories (e.g., homework, exams, group projects) so that I can manage multiple classes efficiently.

As a team leader, I want to create shared mission lists for my team members so that we can collaborate on tasks together in one place.

As a casual user, I want to sort missions by creation date or priority so that I can quickly decide what to do next without overthinking.

As a data-driven user, I want to view my task completion statistics (e.g., success rate, time spent) so that I can track my productivity progress.

As a remote worker, I want to attach useful links or notes to each mission so that I can keep reference materials together with my tasks.

### Leo Fu

As a user, I want to create new tasks with titles and descriptions so that I can keep track of what I need to do.

As a user, I want to edit existing tasks so that I can update details when something changes.

As a user, I want to delete completed or unnecessary tasks so that my to-do list stays clean.

As a user, I want to tag my tasks with keywords so that I can group related items together.

As a user, I want to search tasks by tag or keyword so that I can quickly find specific tasks.

As a user, I want to mark tasks as completed so that I can easily see what I have finished.

As a user, I want my to-do list to be simple and mobile-friendly so that I can check it on my phone anytime.

As an instructor, I want to upload my tasks for my class, so that I won't forget my teaching progress.

As a student, I want to edit and delete my existing tasks, so that I can figure out what I need to do and remove outdated information.

As a student, I want to organize my tasks by course, so that I can easily track assignments and deadlines for each class.

As a tutor, I want to categorize my tasks by the classes I teach, so that I can efficiently plan lessons, track grading deadlines, and manage my workload.

As a working professional, I want to create and save meeting notes, so that I can keep a clear record of what was discussed and decided in each meeting.

As a busy worker, I want to write notes as to-do lists, so that I don’t forget important tasks and can easily track my progress.

### Hanqi Gui

As a user, I want to categorize my weekly tasks by life area (e.g., fitness, study, work, personal) so that I can balance my time across different aspects of my life.

As a user, I want to set specific days for each task so that I can clearly see what needs to be done on each day of the week.

As a user, I want to view my weekly tasks in a single dashboard or calendar view so that I can get an overview of my entire week at a glance.

As a user, I want to receive reminders or notifications for upcoming tasks so that I don’t miss important activities during the week.

As a user, I want to track my progress for each category (e.g., how many gym sessions completed, how many assignments done) so that I can stay motivated and measure my consistency.

As a user, I want to carry unfinished tasks from the previous week into the new week automatically so that I don’t lose track of tasks I haven’t completed yet.

## Steps necessary to run the software

Make sure you have already installed python, pip, and pipenv.
- **Python 3.10+** → check with `python3 --version`  
  [Download here](https://www.python.org/downloads/) if not installed.
- **pip** → check with `pip --version` (usually included with Python)
- **pipenv** → install with `pip install pipenv`

1) Clone the repository
Enter the following command in your terminal:
git clone https://github.com/swe-students-fall2025/2-web-app-team4swe.git
cd 2-web-app-team4swe

2) Install all required packages listed in requirements.txt
Enter the following command in your terminal:
pipenv install -r requirements.txt

3) Install Mongodb
Enter the following command in your terminal:
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

4) Create the .env file
Enter the following command in your terminal:
cp env.example .env
Then open the created .env file and replace the placeholder values with your own configuration.

5) Run the app
Enter the following command in your terminal:
pipenv run python app.py

6) After running the command, you should see a line like: Running on http://127.0.0.1:5000, open the link generated in your browser to use the app. To stop the app, press Ctrl + C in your terminal.

If run with Docker:
1) Before run the software, you need to
install and run [docker desktop](https://www.docker.com/get-started/)
create a [dockerhub account](https://app.docker.com/signup?)


2) Clone the repository
Enter the following command in your terminal:
git clone https://github.com/swe-students-fall2025/2-web-app-team4swe.git
cd 2-web-app-team4swe


3) Create the .env file
Enter the following command in your terminal:
cp env.example .env
Then open the created .env file and replace the placeholder values with your own configuration.


4) Run the software
Enter the following command in your terminal:
docker compose up --build -d


5) Open the web app
Open your browser and go to:
http://localhost:5000


If you see an error message saying that a particular port is already in use, you can assign a different port for the Flask app in your docker-compose.yml file.
To do so, edit the first number in the ports section, for example:
services:
 flask-app:
   ports:
     - "10000:5000" 
This means the app will now run on port 10000 on your computer, then you could visit http://localhost:10000
If you edit any file in the project, you must stop and restart the containers for the changes to take effect:
docker compose down
docker compose up --build -d


6) Stop the app
Enter the following command in your terminal:
docker compose down


## Task boards

See instructions. Delete this line and place a link to the task boards here.
