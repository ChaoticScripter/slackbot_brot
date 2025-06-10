#==========================
# run.py
#==========================

from app.routes import flask_app
from db import init_db
from app.scheduler import init_scheduler

if __name__ == "__main__":
    init_db()
    scheduler = init_scheduler()
    flask_app.run(host="0.0.0.0", port=3000, debug=False)