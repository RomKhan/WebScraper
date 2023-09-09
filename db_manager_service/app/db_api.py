import datetime
import logging
import threading

from fastapi import APIRouter

from KeysEnum import KeysEnum
from db_utils import *

router = APIRouter()
image_reuests_count = 0


@router.post('/saveListing', status_code=200)
async def save_db(request_json: dict):
    offers = request_json['offers']
    for offer in offers:
        offer[KeysEnum.DESAPEAR_DATE.value] = datetime.date.today()
    dataworker = await get_dataworker()
    new_count = await dataworker.save_to_db(offers)

    return f'{new_count}'


@router.get('/getWebsiteId', status_code=200)
async def get_website_id(website: str):
    dataworker = await get_dataworker()
    return str(await dataworker.get_by_condition('Websites', 'website_id', website, 'website_name'))


@router.get('/getCityId', status_code=200)
async def get_city_id(city: str):
    dataworker = await get_dataworker()
    return str(await dataworker.get_by_condition('Cities', 'city_id', city, 'city_name'))


@router.get('/getListingTypeId', status_code=200)
async def get_listing_type_id(listing_type: str):
    dataworker = await get_dataworker()
    id = await dataworker.get_by_condition('Listing_Type', 'listing_type_id', listing_type, 'listing_type_name')
    if listing_type == 'sale':
        dataworker.sale_id = id
    elif listing_type == 'rent':
        dataworker.rent_id = id
    return str(id)

@router.post('/saveImages', status_code=200)
async def load_images(data: dict):
    image_loader = get_image_loader()
    platform_name, offer_id, images_url = data['website_name'], data['id'], data['urls']
    for i in range(len(images_url)):
        image_data = {'website_name': platform_name, 'id': offer_id, 'url': images_url, 'index': i}
        image_loader.image_queue.append(image_data)
    # image_loader.load_images_to_disk(data)
    # thread = threading.Thread(image_loader.load_images_to_disk, args=(data))
    # thread.start()
    # global image_reuests_count
    # image_reuests_count += 1
    # if image_reuests_count == 100:
    #     image_reuests_count = 0
    #     thread = threading.Thread(image_loader.download_current_state)
    #     thread.start()
    return 'Data saved successfully'

# @router.get('/pullImages', status_code=200)
# async def pull_images():
#     image_loader = get_image_loader()
#     await image_loader.download_current_state()
#     return 'Data saved successfully'

