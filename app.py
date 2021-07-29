import atexit
from datetime import datetime

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

from ingest import ingest_new_games
from ingest.parser import GameEventParser

app = Flask(__name__)

parser = GameEventParser()
ingest_new_games(parser)

scheduler = BackgroundScheduler()
scheduler.add_job(func=ingest_new_games, args=(parser,),
                  name="Ingest new games",
                  trigger="interval", seconds=60, coalesce=True,
                  max_instances=1, next_run_time=datetime.now())
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
