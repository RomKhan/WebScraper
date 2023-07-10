import atexit
import os

from flask import Flask
from flask_apscheduler import APScheduler
import db_api
from db_utils import *


def teardown_db():
    get_db_connect().close()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.register_blueprint(db_api.bp)

    @app.route("/ping")
    def ping():
        return "OK!"

    return app


app = create_app()

if __name__ == '__main__':
    atexit.register(teardown_db)
    scheduler = APScheduler()
    scheduler.add_job(id='my_job', func=get_image_loader().download_current_state, trigger='interval', seconds=60)
    scheduler.init_app(app)
    scheduler.start()
    if not os.path.exists('cian'):
        os.mkdir('cian')
    if not os.path.exists('domclick'):
        os.mkdir('domclick')
    if not os.path.exists('avito'):
        os.mkdir('avito')
    app.run(host='0.0.0.0', port=8080)
