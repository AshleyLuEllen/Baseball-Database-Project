from app import app, db
from app.models import Batting


@app.shell_context_processor
def make_shell_context():
    return{'db': db, 'Batting': Batting}
