# DevTrack - Developer Task Manager

A Flask-based task manager with SQLite, built in 3 days.

## Features
- Create tasks with title, description, priority, deadline
- Status: To Do, In Progress, Completed
- Search and filter tasks
- Dashboard stats (total, pending, in-progress, completed)
- Edit / Delete
- REST API + Automated tests

## Tech Stack
Python, Flask, SQLite, HTML, CSS, JavaScript, Pytest

## How to run
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python database.py
python app.py

Open http://127.0.0.1:5000

## API Endpoints
- GET /api/tasks
- POST /api/tasks
- PUT /api/tasks/<id>
- DELETE /api/tasks/<id>
- GET /api/stats

## Tests
python -m pytest -v