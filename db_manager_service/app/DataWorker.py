import asyncio
import copy
import logging

from KeysEnum import KeysEnum


class DataWorker:
    def __init__(self, async_pull, address_manager):
        self.rent_id = None
        self.sale_id = None
        self.seller_keys = ['Название продаца', 'Тип продаца']
        self.lisitng_type_keys = ['Тип обьявления']
        self.adress_keys = [KeysEnum.ADDRESS_ID.value, 'Адресс', KeysEnum.CITY_ID.value]
        self.house_fetures_keys = [
            'Этажей в доме',
            'Строительная серия',
            'Пассажирский лифт',
            'Грузовой лифт',
            'Парковка',
            'Подъезды',
            'Аварийность',
            'Тип дома',
            'Газоснабжение',
            'Мусоропровод',
            'Консьерж',
            'Год постройки',
            'Год сдачи',
            'Двор',
            'Тип перекрытий',
            'Дом',
            'Название ЖК',
            'Количество квартир'
        ]
        self.listings_static_keys = [
            KeysEnum.LISTING_ID.value,
            KeysEnum.LISTING_TYPE_ID.value,
            KeysEnum.ADDRESS_ID.value,
            'Число комнат',
            'Тип жилья',
            'Общая площадь',
            'Жилая площадь',
            'Площадь кухни',
            'Этаж квартиры',
            'Высота потолков',
            'Вид из окон',
            'Ремонт',
            'Отопление',
            'Совмещенный санузел',
            'Раздельный санузел',
            'Лоджия',
            'Балкон',
            'Отделка',
            'Мебель',
            'Техника',
            'Теплый пол',
            'Лет в собственности',
            'Количество собственников',
            'Несовершеннолетние собственники',
            'Прописанные несовершеннолетние',
            'Перепланировка',
            KeysEnum.APPEARING_DATE.value,
            KeysEnum.DESAPEAR_DATE.value,
            'Тип комнат'
        ]
        self.listings_keys = [
            KeysEnum.LISTING_ID.value,
            KeysEnum.PRICE.value,
            KeysEnum.DESAPEAR_DATE.value,
            'Торг',
            'Онлайн показ',
            'Описание'
        ]
        self.lisitng_sale_keys = [
            KeysEnum.LISTING_ID.value,
            'Условия сделки',
            'Ипотека'
        ]
        self.lisitng_rent_keys = [
            KeysEnum.LISTING_ID.value,
            'Коммуналньые платежи',
            'Комиссия',
            'Предоплата',
            'Залог',
            'Срок аренды'
        ]
        self.website_listings_map_keys = [
            'Ссылка'
        ]
        self.listings_images_keys = [
            'Путь к картинкам'
        ]
        self.not_changed_keys = ['appearing_date']
        self.async_pull = async_pull
        self.address_manager = address_manager
        # self.sync_db_conn = sync_db_conn
        self.address_pull = []
        self.lock = False

    async def insert_many(self, query, records):
        async with self.async_pull.acquire() as connection:
            async with connection.transaction():
                await connection.executemany(query, records)

    async def query_with_returning(self, query, records=None):
        async with self.async_pull.acquire() as connection:
            async with connection.transaction():
                if records is not None:
                    return await connection.fetch(query, records)
                else:
                    return await connection.fetch(query)

    async def get_by_condition(self, talbe, table_id, condition_value, condition_column):
        while self.lock:
            await asyncio.sleep(0.1)
        self.lock = True
        select_query = f"""
                SELECT {table_id} FROM {talbe} WHERE {condition_column}='{condition_value}'
            """
        values = await self.query_with_returning(select_query)

        if len(values) != 0:
            self.lock = False
            return values[0][f'{table_id}']
        else:
            insert_query = f"""
                    INSERT INTO {talbe} ({condition_column})
                    VALUES ($1)
                    RETURNING {table_id}
                """

            record_to_insert = (condition_value,)
            values = await self.query_with_returning(insert_query, *record_to_insert)

            self.lock = False
            return values[0][f'{table_id}']

    async def update_or_past(self, keys, new_records, id_name, table_name, history_keys = None):
        idx_all = set([row[0] for row in new_records])
        existed_rows = []
        if history_keys is not None:
            select_query = f"SELECT {', '.join(history_keys)} FROM {table_name} WHERE {id_name} = ANY($1)ORDER BY {id_name}"
            existed_rows = await self.query_with_returning(select_query, list(idx_all))
        idx_exists = set([row[0] for row in existed_rows])


        insert_query = f"""INSERT INTO {table_name} ({", ".join(keys)})
                              VALUES ({", ".join([f"${i+1}" for i in range(len(keys))])})
                              ON CONFLICT ({id_name}) DO
                              UPDATE SET {", ".join([f"{key} = COALESCE(EXCLUDED.{key}, {table_name}.{key})" for key in keys])}"""
        await self.insert_many(insert_query, new_records)

        if history_keys is not None and len(existed_rows) > 0:
            select_query = f"SELECT {', '.join(history_keys)} FROM {table_name} WHERE {id_name} = ANY($1) ORDER BY {id_name}"
            updated_rows = await self.query_with_returning(select_query, list(idx_exists))

            filter_updated_rows = []
            for i in range(len(existed_rows)):
                is_updated = updated_rows[i] == existed_rows[i]
                if not is_updated:
                    filter_updated_rows.append(existed_rows[i])

            if len(filter_updated_rows) > 0:
                insert_changes_query = f"""INSERT INTO {table_name}_Changes ({", ".join(history_keys)})
                                           VALUES ({", ".join([f"${i+1}" for i in range(len(history_keys))])})"""
                await self.insert_many(insert_changes_query, filter_updated_rows)

        return idx_all - idx_exists

    async def update_or_past_seller(self, data):
        records = []
        keys = [KeysEnum.SELLER_NAME.value, KeysEnum.SELLER_TYPE.value]
        for offer in data:
            records.append((offer['Название продаца'], offer['Тип продаца']))
        return await self.update_or_past(keys, records, KeysEnum.SELLER_NAME.value, 'Sellers')

    async def insert_address(self, data):
        select_query = f"""SELECT address_id, latitude, longitude FROM Address
                           WHERE (latitude, longitude)
                           IN ({', '.join([f'{offer[KeysEnum.LATITUDE.value], offer[KeysEnum.LONGITUTE.value]}' for offer in data])})"""
        existed_records = await self.query_with_returning(select_query)
        existed_records = {(record[1], record[2]): record[0] for record in existed_records}
        keys = [KeysEnum.FULL_ADDRESS.value, KeysEnum.CITY_ID.value, KeysEnum.LATITUDE.value, KeysEnum.LONGITUTE.value]
        records = []
        equals = {}
        for i in range(len(data)):
            if (data[i][KeysEnum.LATITUDE.value], data[i][KeysEnum.LONGITUTE.value]) in equals:
                equals[(data[i][KeysEnum.LATITUDE.value], data[i][KeysEnum.LONGITUTE.value])].append(i)
            elif (data[i][KeysEnum.LATITUDE.value], data[i][KeysEnum.LONGITUTE.value]) not in existed_records:
                records.append((
                    data[i][KeysEnum.ADDRESS_ID.value],
                    data[i][KeysEnum.FULL_ADDRESS.value],
                    data[i][KeysEnum.CITY_ID.value],
                    data[i][KeysEnum.LATITUDE.value],
                    data[i][KeysEnum.LONGITUTE.value]
                ))
                equals[(data[i][KeysEnum.LATITUDE.value], data[i][KeysEnum.LONGITUTE.value])] = [i]
            else:
                data[i][KeysEnum.ADDRESS_ID.value] = existed_records[(data[i][KeysEnum.LATITUDE.value], data[i][KeysEnum.LONGITUTE.value])]

        insert_query = f"""INSERT INTO Address ({", ".join(keys)})
                           (SELECT {", ".join([f'r.{key}' for key in keys])}
                           FROM unnest($1::Address[]) as r)
                           RETURNING {KeysEnum.ADDRESS_ID.value}, {KeysEnum.LATITUDE.value}, {KeysEnum.LONGITUTE.value}"""
        addresses = await self.query_with_returning(insert_query, records)

        for address in addresses:
            for i in equals[(address[KeysEnum.LATITUDE.value], address[KeysEnum.LONGITUTE.value])]:
                data[i][KeysEnum.ADDRESS_ID.value] = address[KeysEnum.ADDRESS_ID.value]

    async def insert_address_match(self, data):
        keys = ['website_address', 'real_address_id']
        records = []
        for offer in data:
            records.append([offer['Адресс'], offer[KeysEnum.ADDRESS_ID.value]])

        await self.update_or_past(keys, records, 'website_address', 'Address_Match')

    async def patch_address(self, lat, lon, full_address, offer):
        while self.lock:
            await asyncio.sleep(0.05)
        self.lock = True

        offer[KeysEnum.FULL_ADDRESS.value] = full_address
        if lat is not None and lon is not None:
            offer[KeysEnum.LATITUDE.value] = float(lat)
            offer[KeysEnum.LONGITUTE.value] = float(lon)
        else:
            self.lock = False
            return
        self.address_pull.append(offer)
        if len(self.address_pull) < 5:
            self.lock = False
            return

        await self.insert_address(self.address_pull)
        await self.insert_address_match(self.address_pull)
        await self.update_or_past_house(self.address_pull)
        await self.update_or_past_listings_static_features(self.address_pull)
        self.address_pull = []
        self.lock = False


    async def add_address_ids(self, data):
        addresses = []
        for offer in data:
            addresses.append(offer['Адресс'])

        select_query = f"""
            SELECT * FROM Address_Match WHERE website_address = ANY($1)
        """
        values = await self.query_with_returning(select_query, addresses)
        values = {row[0]: row[1] for row in values}

        not_found = []
        found = []
        if len(values) == 0:
            not_found = data
        else:
            for i in range(len(data)):
                if data[i]['Адресс'] in values:
                    data[i][KeysEnum.ADDRESS_ID.value] = values[data[i]['Адресс']]
                    found.append(data[i])
                else:
                    offer = copy.deepcopy(data[i])
                    for key in list(set(offer.keys()) - (set(self.adress_keys) | set(self.house_fetures_keys) | set(self.listings_static_keys))):
                        del offer[key]
                    not_found.append(offer)
        return not_found, found

    async def update_or_past_house(self, data):
        records = []
        keys = [KeysEnum.ADDRESS_ID.value,
                KeysEnum.MAX_FLOOR.value,
                KeysEnum.HOUSE_SERIE.value,
                KeysEnum.PASSENGER_ELEVATOR_COUNT.value,
                KeysEnum.FREIGHT_ELEVATOR_COUNT.value,
                KeysEnum.PARKING_TYPE.value,
                KeysEnum.ENTRANCE_COUNT.value,
                KeysEnum.IS_DERELICTED.value,
                KeysEnum.HOUSE_TYPE.value,
                KeysEnum.GAS_SUPPLY_TYPE.value,
                KeysEnum.IS_CHUTE.value,
                KeysEnum.CONCIERGE.value,
                KeysEnum.END_BUILD_YEAR.value,
                KeysEnum.YARD_DATA.value,
                KeysEnum.FLOORING_TYPE.value,
                KeysEnum.HOUSE_STATUS.value,
                KeysEnum.RESIDENTIAL_COMPLEX_NAME.value,
                KeysEnum.APARTMENTS_NUMBER.value
                ]
        for offer in data:
            records.append((offer[KeysEnum.ADDRESS_ID.value],
                            offer['Этажей в доме'],
                            offer['Строительная серия'],
                            offer['Пассажирский лифт'],
                            offer['Грузовой лифт'],
                            offer['Парковка'],
                            offer['Подъезды'],
                            offer['Аварийность'],
                            offer['Тип дома'],
                            offer['Газоснабжение'],
                            offer['Мусоропровод'],
                            offer['Консьерж'],
                            offer['Год постройки'] if offer['Год постройки'] is not None else offer['Год сдачи'],
                            offer['Двор'],
                            offer['Тип перекрытий'],
                            offer['Дом'],
                            offer['Название ЖК'],
                            offer['Количество квартир']
                            ))
        history_keys = [KeysEnum.ADDRESS_ID.value, KeysEnum.END_BUILD_YEAR.value, KeysEnum.HOUSE_STATUS.value, KeysEnum.IS_DERELICTED.value]
        await self.update_or_past(keys, records, KeysEnum.ADDRESS_ID.value, 'House', history_keys)

    async def update_or_past_listings_static_features(self, data):
        records = []
        keys = [KeysEnum.LISTINGS_STATIC_FEATURES_ID.value,
                KeysEnum.LISTING_TYPE_ID.value,
                KeysEnum.ADDRESS_ID.value,
                KeysEnum.ROOM_COUNT.value,
                KeysEnum.PROPERTY_TYPE.value,
                KeysEnum.TOTAL_AREA.value,
                KeysEnum.LIVING_AREA.value,
                KeysEnum.KITCHEN_AREA.value,
                KeysEnum.APARTMENT_FLOOR.value,
                KeysEnum.CEILING_HEIGHT.value,
                KeysEnum.WINDOW_VIEW.value,
                KeysEnum.RENOVATION.value,
                KeysEnum.HEATING_TYPE.value,
                KeysEnum.COMBINED_BATHROOM_COUNT.value,
                KeysEnum.SEPARATE_BATHROOM_COUNT.value,
                KeysEnum.LOGGIA_COUNT.value,
                KeysEnum.BALCONY_COUNT.value,
                KeysEnum.DECORATION_FINISHING_TYPE.value,
                KeysEnum.FURNITURE.value,
                KeysEnum.TECHNIQUE.value,
                KeysEnum.HEATED_FLOORS.value,
                KeysEnum.YEARS_OWNED.value,
                KeysEnum.OWNERS_COUNT.value,
                KeysEnum.MINOR_OWNERS.value,
                KeysEnum.REGISTERED_MINORS.value,
                KeysEnum.REDEVELOPMENT.value,
                KeysEnum.DESAPEAR_DATE.value,
                KeysEnum.ROOMS_TYPE.value
                ]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value],
                            offer[KeysEnum.LISTING_TYPE_ID.value],
                            offer[KeysEnum.ADDRESS_ID.value],
                            offer['Число комнат'],
                            offer['Тип жилья'],
                            offer['Общая площадь'],
                            offer['Жилая площадь'],
                            offer['Площадь кухни'],
                            offer['Этаж квартиры'],
                            offer['Высота потолков'],
                            offer['Вид из окон'],
                            offer['Ремонт'],
                            offer['Отопление'],
                            offer['Совмещенный санузел'],
                            offer['Раздельный санузел'],
                            offer['Лоджия'],
                            offer['Балкон'],
                            offer['Отделка'],
                            offer['Мебель'],
                            offer['Техника'],
                            offer['Теплый пол'],
                            offer['Лет в собственности'],
                            offer['Количество собственников'],
                            offer['Несовершеннолетние собственники'],
                            offer['Прописанные несовершеннолетние'],
                            offer['Перепланировка'],
                            offer[KeysEnum.DESAPEAR_DATE.value],
                            offer['Тип комнат']
                            ))
        return await self.update_or_past(keys, records, KeysEnum.LISTINGS_STATIC_FEATURES_ID.value, 'Listings_Static_Features')

    async def update_or_past_listings(self, data):
        records = []
        keys = [KeysEnum.LISTING_ID.value,
                KeysEnum.SELLER_NAME.value,
                KeysEnum.DESCRIPTION.value,
                KeysEnum.PRICE.value,
                KeysEnum.ONLINE_VIEW.value,
                KeysEnum.NEGOTIATION.value
                ]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value],
                            offer['Название продаца'],
                            offer['Описание'],
                            offer[KeysEnum.PRICE.value],
                            offer['Торг'],
                            offer['Онлайн показ']
                            ))
        history_keys = [KeysEnum.LISTING_ID.value,
                        KeysEnum.SELLER_NAME.value,
                        KeysEnum.DESCRIPTION.value,
                        KeysEnum.PRICE.value,
                        KeysEnum.ONLINE_VIEW.value,
                        KeysEnum.NEGOTIATION.value
                        ]
        idx = await self.update_or_past(keys, records, KeysEnum.LISTING_ID.value, 'Listings', history_keys)
        new_rows = []
        for offer in data:
            if offer[KeysEnum.LISTING_ID.value] in idx:
                new_rows.append(offer)
        return new_rows

    async def update_or_past_listings_sale(self, data):
        records = []
        keys = [KeysEnum.LISTINGS_SALE_ID.value,
                KeysEnum.CONDITIONS.value,
                KeysEnum.IS_MORTGAGE_AVAILABLE.value
                ]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value],
                            offer['Условия сделки'],
                            offer['Ипотека']
                            ))
        history_keys = [KeysEnum.LISTINGS_SALE_ID.value,
                        KeysEnum.CONDITIONS.value,
                        KeysEnum.IS_MORTGAGE_AVAILABLE.value]
        return await self.update_or_past(keys, records, KeysEnum.LISTINGS_SALE_ID.value, 'Listings_Sale', history_keys)

    async def update_or_past_listings_rent(self, data):
        records = []
        keys = [KeysEnum.LISTINGS_RENT_ID.value,
                KeysEnum.RENTAL_PERIOD.value,
                KeysEnum.IS_COMMUNAL_PAYMENTS_INCLUDED.value,
                KeysEnum.PLEDGE.value,
                KeysEnum.COMMISSION.value,
                KeysEnum.PREPAYMENT.value]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value],
                            offer['Срок аренды'],
                            offer['Коммуналньые платежи'],
                            offer['Залог'],
                            offer['Комиссия'],
                            offer['Предоплата']))

        history_keys = [KeysEnum.LISTINGS_RENT_ID.value,
                        KeysEnum.IS_COMMUNAL_PAYMENTS_INCLUDED.value,
                        KeysEnum.PLEDGE.value,
                        KeysEnum.COMMISSION.value,
                        KeysEnum.PREPAYMENT.value]
        return await self.update_or_past(keys, records, KeysEnum.LISTINGS_RENT_ID.value, 'Listings_Rent', history_keys)

    async def update_or_past_websites_listings_map(self, data):
        records = []
        keys = [KeysEnum.LISTING_ID.value, KeysEnum.WEBSITE_ID.value, KeysEnum.LINK_URL.value]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value], offer[KeysEnum.WEBSITE_ID.value], offer['Ссылка']))

        await self.update_or_past(keys, records, 'map_id', 'Websites_Listings_Map')

    async def update_or_past_listing_images(self, data):
        records = []
        keys = [KeysEnum.LISTING_ID.value, KeysEnum.IMAGE_PATH.value]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value], offer['Путь к картинкам']))

        await self.update_or_past(keys, records, 'image_id', 'Listing_Images')

    def data_dict_flatten(self, data):
        for key in list(data.keys()):
            if type(data[key]) is dict:
                for sub_key in data[key]:
                    data[sub_key] = data[key][sub_key]
                data.pop(key)

    @staticmethod
    def type_convert_if_possible(data, field, type):
        try:
            value = data[field].replace(',', '.')
            return type(value)
        except Exception as e:
            return None

    def add_none_fields(self, data):
        possible_keys = set(self.seller_keys) |\
                        set(self.lisitng_type_keys) |\
                        set(self.adress_keys) |\
                        set(self.house_fetures_keys) |\
                        set(self.listings_static_keys) |\
                        set(self.listings_keys) | \
                        set(self.website_listings_map_keys) |\
                        set(self.listings_images_keys)
        if data[KeysEnum.LISTING_TYPE_ID.value] == self.sale_id:
            possible_keys |= set(self.lisitng_sale_keys)
        else:
            possible_keys |= set(self.lisitng_rent_keys)

        for key in possible_keys:
            if key not in data.keys():
                data[key] = None

    def type_convert(self, data):
        data[KeysEnum.PRICE.value] = DataWorker.type_convert_if_possible(data, KeysEnum.PRICE.value, int)
        data['Число комнат'] = DataWorker.type_convert_if_possible(data, 'Число комнат', int)
        data['Общая площадь'] = DataWorker.type_convert_if_possible(data, 'Общая площадь', float)
        data['Жилая площадь'] = DataWorker.type_convert_if_possible(data, 'Жилая площадь', float)
        data['Площадь кухни'] = DataWorker.type_convert_if_possible(data, 'Площадь кухни', float)
        data['Этаж квартиры'] = DataWorker.type_convert_if_possible(data, 'Этаж квартиры', int)
        data['Этажей в доме'] = DataWorker.type_convert_if_possible(data, 'Этажей в доме', int)
        data['Год постройки'] = DataWorker.type_convert_if_possible(data, 'Год постройки', int)
        data['Подъезды'] = DataWorker.type_convert_if_possible(data, 'Подъезды', int)
        data['Высота потолков'] = DataWorker.type_convert_if_possible(data, 'Высота потолков', float)
        data['Год сдачи'] = DataWorker.type_convert_if_possible(data, 'Год сдачи', int)
        data['Совмещенный санузел'] = DataWorker.type_convert_if_possible(data, 'Совмещенный санузел', int)
        data['Раздельный санузел'] = DataWorker.type_convert_if_possible(data, 'Раздельный санузел', int)
        data['Лоджия'] = DataWorker.type_convert_if_possible(data, 'Лоджия', int)
        data['Балкон'] = DataWorker.type_convert_if_possible(data, 'Балкон', int)
        data['Пассажирский лифт'] = DataWorker.type_convert_if_possible(data, 'Пассажирский лифт', int)
        data['Грузовой лифт'] = DataWorker.type_convert_if_possible(data, 'Грузовой лифт', int)
        data['Количество собственников'] = DataWorker.type_convert_if_possible(data, 'Количество собственников', int)
        data['Количество квартир'] = DataWorker.type_convert_if_possible(data, 'Количество квартир', int)

    async def save_to_db(self, data):
        offers_with_sellers = []
        is_sale = True if data[0][KeysEnum.LISTING_TYPE_ID.value] == self.sale_id else False
        for offer in data:
            self.data_dict_flatten(offer)
            self.add_none_fields(offer)
            self.type_convert(offer)
            if offer['Название продаца'] is not None:
                offers_with_sellers.append(offer)

        await self.update_or_past_seller(offers_with_sellers)
        not_found, found = await self.add_address_ids(data)
        for offer in not_found:
            self.address_manager.address_queue.put(offer)
        await self.update_or_past_house(found)
        await self.update_or_past_listings_static_features(data)
        new_rows = await self.update_or_past_listings(data)
        if is_sale:
            await self.update_or_past_listings_sale(data)
        else:
            await self.update_or_past_listings_rent(data)

        await self.update_or_past_websites_listings_map(new_rows)
        await self.update_or_past_listing_images(new_rows)
        return len(new_rows)
