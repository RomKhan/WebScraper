import datetime

from flask import Blueprint, request

from KeysEnum import KeysEnum
from db_utils import *

bp = Blueprint("db", __name__, url_prefix="/db")


@bp.route('/saveListing', methods=['POST'])
def save_db():
    data = request.json
    data[KeysEnum.APPEARING_DATE.value] = datetime.date.today()
    data[KeysEnum.DESAPEAR_DATE.value] = datetime.date.today()
    dataworker = get_dataworker()
    dataworker.data_dict_flatten(data)
    dataworker.add_none_fields(data)
    dataworker.type_convert(data)
    if data['Название продаца'] is not None:
        dataworker.update_or_past_seller(data)
    dataworker.update_or_past_addres(data)
    dataworker.update_or_past_house_features(data)
    dataworker.update_or_past_listings_static_features(data)
    is_new = dataworker.update_or_past_listings(data)
    if data[KeysEnum.LISTING_TYPE_ID.value] == 1:
        dataworker.update_or_past_listings_sale(data)
    else:
        dataworker.update_or_past_listings_rent(data)

    if is_new:
        dataworker.update_or_past_websites_listings_map(data)
        dataworker.update_or_past_listing_images(data)
    return 'Data saved successfully'


@bp.route('/getWebsiteId', methods=['GET'])
def get_website_id():
    website_name = request.args.get('website')
    dataworker = get_dataworker()
    return str(dataworker.get_id_by_condition('Websites', 'website_id', website_name, 'website_name'))


@bp.route('/getCityId', methods=['GET'])
def get_city_id():
    city = request.args.get('city')
    dataworker = get_dataworker()
    return str(dataworker.get_id_by_condition('Cities', 'city_id', city, 'city_name'))


@bp.route('/getListingTypeId', methods=['GET'])
def get_listing_type_id():
    listing_type = request.args.get('listing_type')
    dataworker = get_dataworker()
    return str(dataworker.get_id_by_condition('Listing_Type', 'listing_type_id', listing_type, 'listing_type_name'))

# @bp.route('/getPriceWindows', methods=['GET'])
# def get_price_windows():
#     website_id = request.args.get('website_id')
#     max_listings = request.args.get('max_listings')
#     dataworker = get_dataworker()
#     return str(dataworker.get_price_windows(website_id, max_listings))

@bp.route('/saveImages', methods=['POST'])
def load_images():
    data = request.json
    image_loader = get_image_loader()
    image_loader.load_images_to_disk(data)
    return 'Data saved successfully'

