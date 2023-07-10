import psycopg2
from flask import current_app
from yadisk import yadisk

from DataWorker import DataWorker
from ImageLoader import ImageLoader

dataworker = None
db_conn = None
image_loader = None


def get_dataworker():
    global dataworker
    if dataworker is None:
        dataworker = DataWorker(get_db_connect())
    return dataworker


def get_db_connect():
    global db_conn
    if db_conn is None:
        db_host = current_app.config['DB_HOST']
        db_port = current_app.config['DB_PORT']
        db_name = current_app.config['DB_NAME']
        db_user = current_app.config['DB_USER']
        db_password = current_app.config['DB_PASSWORD']

        db_conn = psycopg2.connect(user=db_user,
                                   password=db_password,
                                   host=db_host,
                                   port=db_port,
                                   database=db_name
                                   )


    return db_conn

def get_image_loader():
    global image_loader
    if image_loader is None:
        disk = yadisk.YaDisk("ec228561582a46baa7c3f88907c0395d", "46145e37e4cf415d8283490af86b6113")
        disk.token = 'y0_AgAAAAANYmzbAAf07QAAAADl13LC72bkYNO7So6osrxeT1dmwOorZhQ'
        image_loader = ImageLoader(disk=disk)
    return image_loader
