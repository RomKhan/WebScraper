import datetime
import logging

from flask import Blueprint, request

from KeysEnum import KeysEnum
from db_utils import *

bp = Blueprint("db", __name__, url_prefix="/db")


@bp.route('/saveListing', methods=['POST'])
async def save_db():
    offers = request.json['offers']
    for offer in offers:
        offer[KeysEnum.DESAPEAR_DATE.value] = datetime.date.today()
    dataworker = get_dataworker()
    await dataworker.save_to_db(offers)

    return 'Data saved successfully'


@bp.route('/getWebsiteId', methods=['GET'])
async def get_website_id():
    website_name = request.args.get('website')
    dataworker = get_dataworker()
    return str(await dataworker.get_id_by_condition('Websites', 'website_id', website_name, 'website_name'))


@bp.route('/getCityId', methods=['GET'])
async def get_city_id():
    city = request.args.get('city')
    dataworker = get_dataworker()
    return str(await dataworker.get_id_by_condition('Cities', 'city_id', city, 'city_name'))


@bp.route('/getListingTypeId', methods=['GET'])
async def get_listing_type_id():
    listing_type = request.args.get('listing_type')
    dataworker = get_dataworker()
    return str(await dataworker.get_id_by_condition('Listing_Type', 'listing_type_id', listing_type, 'listing_type_name'))


@bp.route('/saveImages', methods=['POST'])
def load_images():
    data = request.json
    image_loader = get_image_loader()
    image_loader.load_images_to_disk(data)
    return 'Data saved successfully'

