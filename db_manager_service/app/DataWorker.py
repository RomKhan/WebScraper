import logging
import time

from KeysEnum import KeysEnum


class DataWorker:
    def __init__(self, db_connection):
        self.seller_keys = ['Название продаца', 'Тип продаца']
        self.lisitng_type_keys = ['Тип обьявления']
        self.adress_keys = ['Адресс', KeysEnum.CITY_ID.value]
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
            'Год постройки',
            'Год сдачи',
            'Тип перекрытий',
            'Дом',
            'Название ЖК',
        ]
        self.listings_static_keys = [
            KeysEnum.LISTING_ID.value,
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
            KeysEnum.APPEARING_DATE.value
        ]
        self.listings_keys = [
            KeysEnum.LISTING_ID.value,
            KeysEnum.PRICE.value,
            KeysEnum.DESAPEAR_DATE.value,
            'Описание'
        ]
        self.lisitng_sale_keys = [
            KeysEnum.LISTING_ID.value,
            'Условия сделки',
            'Ипотека'
        ]
        self.lisitng_rent_keys = [
            KeysEnum.LISTING_ID.value
        ]
        self.website_listings_map_keys = [
            'Ссылка'
        ]
        self.listings_images_keys = [
            'Путь к картинкам'
        ]
        self.not_changed_keys = ['appearing_date']
        self.db_connection = db_connection

    # def get_price_windows(self, website_id, max_listings):
    #     cursor = self.db_connection.cursor()
    #     select_query = f"""
    #                     SELECT MAX(price) AS max_price
    #                     FROM (
    #                         SELECT price,
    #                         (ROW_NUMBER() OVER (ORDER BY price ASC) - 1) / {max_listings} AS win
    #                         FROM Websites_Listings_Map
    #                             JOIN Listings USING(listing_id)
    #                             JOIN Listings_Static_Features ON listing_id = listings_static_features_id
    #                             WHERE website_id = {website_id}
    #                         AND desapear_date = (current_date - INTEGER '0')
    #                         ORDER BY price
    #                         ) AS subquery
    #                     GROUP BY win
    #                     ORDER BY max_price
    #                 """
    #     cursor.execute(select_query)
    #     values = cursor.fetchone()

    async def get_id_by_condition(self, talbe, table_id, condition_value, condition_column):
        cursor = self.db_connection.cursor()

        select_query = f"""
                SELECT {table_id} FROM {talbe} WHERE {condition_column}='{condition_value}'
            """
        cursor.execute(select_query)
        values = cursor.fetchone()

        if values != None:
            cursor.close()
            return values[0]
        else:
            insert_query = f"""
                    INSERT INTO {talbe} ({condition_column})
                    VALUES (%s)
                    RETURNING {table_id}
                """

            record_to_insert = (condition_value,)

            cursor.execute(insert_query, record_to_insert)
            values = cursor.fetchone()
            self.db_connection.commit()
            cursor.close()
            return values[0]

    # def get_if_exist(self, id, id_name, table_name):
    #     cursor = self.db_connection.cursor()
    #     select_query = f"""
    #                 SELECT * FROM {table_name} WHERE {id_name}='{id}'
    #             """
    #     cursor.execute(select_query)
    #     values = cursor.fetchone()
    #
    #     if values is not None:
    #         columns = [desc[0] for desc in cursor.description]
    #         values = dict(zip(columns, values))
    #
    #     cursor.close()
    #
    #     return values
    #
    # def instert_to_db(self, new_record, table_name):
    #     cursor = self.db_connection.cursor()
    #     keys = list(new_record.keys())
    #     values = list(new_record.values())
    #     insert_query = f'INSERT INTO {table_name} ({", ".join(keys)}) VALUES ({", ".join(["%s"] * len(keys))})'
    #     record_to_insert = tuple(values)
    #     cursor.execute(insert_query, record_to_insert)
    #     self.db_connection.commit()
    #     cursor.close()
    #
    # def update_record_db(self, record, new_record, id_name, table_name, history_keys = None):
    #     id = record[id_name]
    #     for key in list(new_record.keys()):
    #         if record[key] == new_record[key] or new_record[key] == None or key in self.not_changed_keys:
    #             new_record.pop(key)
    #             if history_keys is not None and record[key] == None and key in history_keys:
    #                 history_keys.remove(key)
    #
    #     keys = list(new_record.keys())
    #     values = list(new_record.values())
    #     values.append(id)
    #     if history_keys is not None:
    #         history_id = history_keys[0]
    #         history_keys = list(set(keys) & set(history_keys))
    #
    #     if len(new_record) > 0:
    #         cursor = self.db_connection.cursor()
    #         update_query = f'UPDATE {table_name} SET {", ".join([f"{keys[i]} = %s" for i in range(len(keys))])} WHERE {id_name} = %s'
    #         data = tuple(values)
    #         cursor.execute(update_query, data)
    #         self.db_connection.commit()
    #         if history_keys is not None and len(history_keys) > 0:
    #             values = [new_record[key] for key in history_keys]
    #             history_keys.append(history_id)
    #             values.append(id)
    #             insert_query = f'INSERT INTO {table_name}_Changes ({", ".join(history_keys)}) VALUES ({", ".join(["%s"] * len(history_keys))})'
    #             data = tuple(values)
    #             cursor.execute(insert_query, data)
    #             self.db_connection.commit()
    #         cursor.close()

    def update_or_past(self, keys, new_records, id_name, table_name, history_keys = None):
        cursor = self.db_connection.cursor()
        idx_all = set([row[0] for row in new_records])
        existed_rows = []
        if history_keys is not None:
            select_query = f"SELECT {', '.join(history_keys)} FROM {table_name} WHERE {id_name} IN %s ORDER BY {id_name}"
            cursor.execute(select_query, (tuple(idx_all),))
            existed_rows = cursor.fetchall()
        idx_exists = set([row[0] for row in existed_rows])

        insert_query = f"""INSERT INTO {table_name} ({", ".join(keys)})
                              VALUES ({", ".join(["%s"] * len(keys))})
                              ON CONFLICT ({id_name}) DO
                              UPDATE SET {", ".join([f"{key} = EXCLUDED.{key}" for key in keys])}"""
        cursor.executemany(insert_query, new_records)

        if history_keys is not None and len(existed_rows) > 0:
            select_query = f"SELECT {', '.join(history_keys)} FROM {table_name} WHERE {id_name} IN %s ORDER BY {id_name}"
            cursor.execute(select_query, (tuple(idx_exists),))
            updated_rows = cursor.fetchall()

            filter_updated_rows = []
            for i in range(len(existed_rows)):
                is_updated = updated_rows[i] == existed_rows[i]
                if not is_updated:
                    filter_updated_rows.append(existed_rows[i])

            if len(filter_updated_rows) > 0:
                insert_changes_query = f"""INSERT INTO {table_name}_Changes ({", ".join(history_keys)})
                                              VALUES ({", ".join(["%s"] * len(history_keys))})"""
                cursor.executemany(insert_changes_query, filter_updated_rows)

        self.db_connection.commit()
        cursor.close()
        return idx_all - idx_exists

    def update_or_past_seller(self, data):
        records = []
        keys = [KeysEnum.SELLER_NAME.value, KeysEnum.SELLER_TYPE.value]
        for offer in data:
            records.append((offer['Название продаца'], offer['Тип продаца']))
        return self.update_or_past(keys, records, KeysEnum.SELLER_NAME.value, 'Sellers')


    def update_or_past_addres(self, data):
        records = []
        keys = [KeysEnum.ADDRES.value, KeysEnum.CITY_ID.value]
        for offer in data:
            records.append((offer['Адресс'], offer[KeysEnum.CITY_ID.value]))

        return self.update_or_past(keys, records, KeysEnum.ADDRES.value, 'Address')

    def update_or_past_house_features(self, data):
        records = []
        keys = [KeysEnum.ADDRES.value,
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
                KeysEnum.END_BUILD_YEAR.value,
                KeysEnum.FLOORING_TYPE.value,
                KeysEnum.HOUSE_STATUS.value,
                KeysEnum.RESIDENTIAL_COMPLEX_NAME.value
                ]
        for offer in data:
            records.append((offer['Адресс'],
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
                            offer['Год постройки'] if offer['Год постройки'] is not None else offer['Год сдачи'],
                            offer['Тип перекрытий'],
                            offer['Дом'],
                            offer['Название ЖК'],
                            ))
        history_keys = [KeysEnum.ADDRES.value, KeysEnum.END_BUILD_YEAR.value, KeysEnum.HOUSE_STATUS.value, KeysEnum.IS_DERELICTED.value]
        return self.update_or_past(keys, records, KeysEnum.ADDRES.value, 'House_Features', history_keys)

    def update_or_past_listings_static_features(self, data):
        records = []
        keys = [KeysEnum.LISTINGS_STATIC_FEATURES_ID.value,
                KeysEnum.LISTING_TYPE_ID.value,
                KeysEnum.ADDRES.value,
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
                KeysEnum.DESAPEAR_DATE.value
                ]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value],
                            offer[KeysEnum.LISTING_TYPE_ID.value],
                            offer['Адресс'],
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
                            offer[KeysEnum.DESAPEAR_DATE.value],
                            ))
        return self.update_or_past(keys, records, KeysEnum.LISTINGS_STATIC_FEATURES_ID.value, 'Listings_Static_Features')

    def update_or_past_listings(self, data):
        records = []
        keys = [KeysEnum.LISTING_ID.value, KeysEnum.SELLER_NAME.value, KeysEnum.DESCRIPTION.value, KeysEnum.PRICE.value]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value],
                            offer['Название продаца'],
                            offer['Описание'],
                            offer[KeysEnum.PRICE.value]))
        history_keys = [KeysEnum.LISTING_ID.value, KeysEnum.SELLER_NAME.value, KeysEnum.DESCRIPTION.value, KeysEnum.PRICE.value]
        idx = self.update_or_past(keys, records, KeysEnum.LISTING_ID.value, 'Listings', history_keys)
        new_rows = []
        for offer in data:
            if offer[KeysEnum.LISTING_ID.value] in idx:
                new_rows.append(offer)
        return new_rows

    def update_or_past_listings_sale(self, data):
        records = []
        keys = [KeysEnum.LISTINGS_SALE_ID.value, KeysEnum.CONDITIONS.value, KeysEnum.IS_MORTGAGE_AVAILABLE.value]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value],
                            offer['Условия сделки'],
                            offer['Ипотека']))
        history_keys = [KeysEnum.LISTINGS_SALE_ID.value, KeysEnum.CONDITIONS.value, KeysEnum.IS_MORTGAGE_AVAILABLE.value]
        return self.update_or_past(keys, records, KeysEnum.LISTINGS_SALE_ID.value, 'Listings_Sale', history_keys)

    def update_or_past_listings_rent(self, data):
        records = []
        keys = [KeysEnum.LISTINGS_RENT_ID.value]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value]))

        history_keys = [KeysEnum.LISTINGS_RENT_ID.value]
        return self.update_or_past(keys, records, KeysEnum.LISTINGS_RENT_ID.value, 'Listings_Rent', history_keys)

    def update_or_past_websites_listings_map(self, data):
        records = []
        keys = [KeysEnum.LISTING_ID.value, KeysEnum.WEBSITE_ID.value, KeysEnum.LINK_URL.value]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value], offer[KeysEnum.WEBSITE_ID.value], offer['Ссылка']))

        self.update_or_past(keys, records, 'map_id', 'Websites_Listings_Map')

    def update_or_past_listing_images(self, data):
        records = []
        keys = [KeysEnum.LISTING_ID.value, KeysEnum.IMAGE_PATH.value]
        for offer in data:
            records.append((offer[KeysEnum.LISTING_ID.value], offer['Путь к картинкам']))

        self.update_or_past(keys, records, 'image_id', 'Listing_Images')

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
        if data[KeysEnum.LISTING_TYPE_ID.value] == 2:
            possible_keys |= set(self.lisitng_rent_keys)
        else:
            possible_keys |= set(self.lisitng_sale_keys)

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
        data['Высота потолков'] = DataWorker.type_convert_if_possible(data, 'Высота потолков', int)
        data['Год сдачи'] = DataWorker.type_convert_if_possible(data, 'Год сдачи', int)
        data['Совмещенный санузел'] = DataWorker.type_convert_if_possible(data, 'Совмещенный санузел', int)
        data['Раздельный санузел'] = DataWorker.type_convert_if_possible(data, 'Раздельный санузел', int)
        data['Лоджия'] = DataWorker.type_convert_if_possible(data, 'Лоджия', int)
        data['Балкон'] = DataWorker.type_convert_if_possible(data, 'Балкон', int)

    async def save_to_db(self, data):
        offers_with_sellers = []
        is_sale = True if data[0][KeysEnum.LISTING_TYPE_ID.value] == '1' else False
        for offer in data:
            self.data_dict_flatten(offer)
            self.add_none_fields(offer)
            self.type_convert(offer)
            if offer['Название продаца'] is not None:
                offers_with_sellers.append(offer)

        self.update_or_past_seller(offers_with_sellers)
        self.update_or_past_addres(data)
        self.update_or_past_house_features(data)
        self.update_or_past_listings_static_features(data)
        new_rows = self.update_or_past_listings(data)
        if is_sale:
            self.update_or_past_listings_sale(data)
        else:
            self.update_or_past_listings_rent(data)

        self.update_or_past_websites_listings_map(new_rows)
        self.update_or_past_listing_images(new_rows)
        return len(new_rows)



