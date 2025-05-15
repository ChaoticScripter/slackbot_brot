#==========================
# run.py
#==========================
from app.routes import flask_app
from db import init_db

if __name__ == "__main__":
    init_db()
    flask_app.run(host="0.0.0.0", port=3000)