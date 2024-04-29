import asyncio

import asyncpg
import config
from yadisk import yadisk

from DataWorker import DataWorker
from ImageLoader import ImageLoader
from AddressManager import AddressManager

dataworker = None
db_conn = None
image_loader = None
address_manager = None


def get_address_manager():
    global address_manager
    if address_manager is None:
        address_manager = AddressManager(config.dadata_tokens)
    return address_manager

async def get_dataworker():
    global dataworker
    if dataworker is None:
        pool = await get_db_connect()
        address_manager = get_address_manager()
        dataworker = DataWorker(pool, get_address_manager())
        address_manager.dataworker = dataworker
        address_manager.db_loop = asyncio.get_event_loop()
    return dataworker


async def get_db_connect():
    global db_conn
    if db_conn is None:
        db_host = config.DB_HOST
        db_port = config.DB_PORT
        db_name = config.DB_NAME
        db_user = config.DB_USER
        db_password = config.DB_PASSWORD

        dsn = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        pool = await asyncpg.create_pool(dsn)
        if db_conn is None:
            db_conn = pool

    return db_conn

def get_image_loader():
    global image_loader
    if image_loader is None:
        disk = yadisk.YaDisk("ec228561582a46baa7c3f88907c0395d", "46145e37e4cf415d8283490af86b6113")
        disk.token = 'y0_AgAAAAANYmzbAAf07QAAAADl13LC72bkYNO7So6osrxeT1dmwOorZhQ'
        image_loader = ImageLoader(disk=disk)
    return image_loader
