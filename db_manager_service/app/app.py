import atexit
import threading

from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import db_api
from db_utils import *


def teardown_db():
    get_db_connect().close()


def create_app():
    app = FastAPI()
    app.include_router(db_api.router, prefix="/db")

    @app.get("/ping", status_code=200)
    def ping():
        return "I AM OK!"

    return app


app = create_app()
address_save_thread = threading.Thread(target=get_address_manager().address_finder)
address_save_thread.start()
images_save_thread = threading.Thread(target=get_image_loader().load_images_to_disk)
images_save_thread.start()
scheduler = BackgroundScheduler()
scheduler.add_job(get_image_loader().download_current_state, trigger=IntervalTrigger(seconds=60))
scheduler.start()
atexit.register(teardown_db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
