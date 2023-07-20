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

    def get_if_exist(self, id, id_name, table_name):
        cursor = self.db_connection.cursor()
        select_query = f"""
                    SELECT * FROM {table_name} WHERE {id_name}='{id}'
                """
        cursor.execute(select_query)
        values = cursor.fetchone()

        if values is not None:
            columns = [desc[0] for desc in cursor.description]
            values = dict(zip(columns, values))

        cursor.close()

        return values

    def instert_to_db(self, new_record, table_name):
        cursor = self.db_connection.cursor()
        keys = list(new_record.keys())
        values = list(new_record.values())
        insert_query = f'INSERT INTO {table_name} ({", ".join(keys)}) VALUES ({", ".join(["%s"] * len(keys))})'
        record_to_insert = tuple(values)
        cursor.execute(insert_query, record_to_insert)
        self.db_connection.commit()
        cursor.close()

    def update_record_db(self, record, new_record, id_name, table_name, history_keys = None):
        id = record[id_name]
        for key in list(new_record.keys()):
            if record[key] == new_record[key] or new_record[key] == None or key in self.not_changed_keys:
                new_record.pop(key)
                if history_keys is not None and record[key] == None and key in history_keys:
                    history_keys.remove(key)

        keys = list(new_record.keys())
        values = list(new_record.values())
        values.append(id)
        if history_keys is not None:
            history_id = history_keys[0]
            history_keys = list(set(keys) & set(history_keys))

        if len(new_record) > 0:
            cursor = self.db_connection.cursor()
            update_query = f'UPDATE {table_name} SET {", ".join([f"{keys[i]} = %s" for i in range(len(keys))])} WHERE {id_name} = %s'
            data = tuple(values)
            cursor.execute(update_query, data)
            self.db_connection.commit()
            if history_keys is not None and len(history_keys) > 0:
                values = [new_record[key] for key in history_keys]
                history_keys.append(history_id)
                values.append(id)
                insert_query = f'INSERT INTO {table_name}_Changes ({", ".join(history_keys)}) VALUES ({", ".join(["%s"] * len(history_keys))})'
                data = tuple(values)
                cursor.execute(insert_query, data)
                self.db_connection.commit()
            cursor.close()

    def update_or_past(self, new_record, id_name, table_name, history_keys = None):
        record = self.get_if_exist(new_record[id_name], id_name, table_name)
        if record is None and new_record[id_name] is not None:
            self.instert_to_db(new_record, table_name)
            return True
        elif new_record[id_name] is not None:
            self.update_record_db(record, new_record, id_name, table_name, history_keys)
            return False

    def update_or_past_seller(self, data):
        record = {
            KeysEnum.SELLER_NAME.value: data['Название продаца'],
            KeysEnum.SELLER_TYPE.value: data['Тип продаца'],
        }
        return self.update_or_past(record, KeysEnum.SELLER_NAME.value, 'Sellers')

    def update_or_past_addres(self, data):
        record = {
            KeysEnum.ADDRES.value: data['Адресс'],
            KeysEnum.CITY_ID.value: data[KeysEnum.CITY_ID.value]
        }
        return self.update_or_past(record, KeysEnum.ADDRES.value, 'Address')

    def update_or_past_house_features(self, data):
        record = {
            KeysEnum.ADDRES.value: data['Адресс'],
            KeysEnum.MAX_FLOOR.value: data['Этажей в доме'],
            KeysEnum.HOUSE_SERIE.value: data['Строительная серия'],
            KeysEnum.PASSENGER_ELEVATOR_COUNT.value: data['Пассажирский лифт'],
            KeysEnum.FREIGHT_ELEVATOR_COUNT.value: data['Грузовой лифт'],
            KeysEnum.PARKING_TYPE.value: data['Парковка'],
            KeysEnum.ENTRANCE_COUNT.value: data['Подъезды'],
            KeysEnum.IS_DERELICTED.value: data['Аварийность'],
            KeysEnum.HOUSE_TYPE.value: data['Тип дома'],
            KeysEnum.GAS_SUPPLY_TYPE.value: data['Газоснабжение'],
            KeysEnum.IS_CHUTE.value: data['Мусоропровод'],
            KeysEnum.END_BUILD_YEAR.value: data['Год постройки'] if data['Год постройки'] is not None else data['Год сдачи'],
            KeysEnum.FLOORING_TYPE.value: data['Тип перекрытий'],
            KeysEnum.HOUSE_STATUS.value: data['Дом'],
            KeysEnum.RESIDENTIAL_COMPLEX_NAME.value: data['Название ЖК'],
        }
        history_keys = [KeysEnum.ADDRES.value, KeysEnum.END_BUILD_YEAR.value, KeysEnum.HOUSE_STATUS.value, KeysEnum.IS_DERELICTED.value]
        return self.update_or_past(record, KeysEnum.ADDRES.value, 'House_Features', history_keys)

    def update_or_past_listings_static_features(self, data):
        record = {
            KeysEnum.LISTINGS_STATIC_FEATURES_ID.value: data[KeysEnum.LISTING_ID.value],
            KeysEnum.LISTING_TYPE_ID.value: data[KeysEnum.LISTING_TYPE_ID.value],
            KeysEnum.ADDRES.value: data['Адресс'],
            KeysEnum.ROOM_COUNT.value: data['Число комнат'],
            KeysEnum.PROPERTY_TYPE.value: data['Тип жилья'],
            KeysEnum.TOTAL_AREA.value: data['Общая площадь'],
            KeysEnum.LIVING_AREA.value: data['Жилая площадь'],
            KeysEnum.KITCHEN_AREA.value: data['Площадь кухни'],
            KeysEnum.APARTMENT_FLOOR.value: data['Этаж квартиры'],
            KeysEnum.CEILING_HEIGHT.value: data['Высота потолков'],
            KeysEnum.WINDOW_VIEW.value: data['Вид из окон'],
            KeysEnum.RENOVATION.value: data['Ремонт'],
            KeysEnum.HEATING_TYPE.value: data['Отопление'],
            KeysEnum.COMBINED_BATHROOM_COUNT.value: data['Совмещенный санузел'],
            KeysEnum.SEPARATE_BATHROOM_COUNT.value: data['Раздельный санузел'],
            KeysEnum.LOGGIA_COUNT.value: data['Лоджия'],
            KeysEnum.BALCONY_COUNT.value: data['Балкон'],
            KeysEnum.DECORATION_FINISHING_TYPE.value: data['Отделка'],
            KeysEnum.APPEARING_DATE.value: data[KeysEnum.APPEARING_DATE.value],
            KeysEnum.DESAPEAR_DATE.value: data[KeysEnum.DESAPEAR_DATE.value]
        }
        return self.update_or_past(record, KeysEnum.LISTINGS_STATIC_FEATURES_ID.value, 'Listings_Static_Features')

    def update_or_past_listings(self, data):
        record = {
            KeysEnum.LISTING_ID.value: data[KeysEnum.LISTING_ID.value],
            KeysEnum.SELLER_NAME.value: data['Название продаца'],
            KeysEnum.DESCRIPTION.value: data['Описание'],
            KeysEnum.PRICE.value: data[KeysEnum.PRICE.value],
        }
        history_keys = [KeysEnum.LISTING_ID.value, KeysEnum.SELLER_NAME.value, KeysEnum.DESCRIPTION.value, KeysEnum.PRICE.value]
        return self.update_or_past(record, KeysEnum.LISTING_ID.value, 'Listings', history_keys)

    def update_or_past_listings_sale(self, data):
        record = {
            KeysEnum.LISTINGS_SALE_ID.value: data[KeysEnum.LISTING_ID.value],
            KeysEnum.CONDITIONS.value: data['Условия сделки'],
            KeysEnum.IS_MORTGAGE_AVAILABLE.value: data['Ипотека'],
        }
        history_keys = [KeysEnum.LISTINGS_SALE_ID.value, KeysEnum.CONDITIONS.value, KeysEnum.IS_MORTGAGE_AVAILABLE.value]
        return self.update_or_past(record, KeysEnum.LISTINGS_SALE_ID.value, 'Listings_Sale', history_keys)

    def update_or_past_listings_rent(self, data):
        record = {
            KeysEnum.LISTINGS_RENT_ID.value: data[KeysEnum.LISTING_ID.value]
        }
        history_keys = [KeysEnum.LISTINGS_RENT_ID.value]
        return self.update_or_past(record, KeysEnum.LISTINGS_RENT_ID.value, 'Listings_Rent', history_keys)

    def update_or_past_websites_listings_map(self, data):
        record = {
            KeysEnum.LISTING_ID.value: data[KeysEnum.LISTING_ID.value],
            KeysEnum.WEBSITE_ID.value: data[KeysEnum.WEBSITE_ID.value],
            KeysEnum.LINK_URL.value: data['Ссылка'],
        }
        self.instert_to_db(record, 'Websites_Listings_Map')

    def update_or_past_listing_images(self, data):
        record = {
            KeysEnum.LISTING_ID.value: data[KeysEnum.LISTING_ID.value],
            KeysEnum.IMAGE_PATH.value: data['Путь к картинкам']
        }
        self.instert_to_db(record, 'Listing_Images')

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
        self.data_dict_flatten(data)
        self.add_none_fields(data)
        self.type_convert(data)
        if data['Название продаца'] is not None:
            self.update_or_past_seller(data)
        self.update_or_past_addres(data)
        self.update_or_past_house_features(data)
        self.update_or_past_listings_static_features(data)
        is_new = self.update_or_past_listings(data)
        if data[KeysEnum.LISTING_TYPE_ID.value] == 1:
            self.update_or_past_listings_sale(data)
        else:
            self.update_or_past_listings_rent(data)

        if is_new:
            self.update_or_past_websites_listings_map(data)
            self.update_or_past_listing_images(data)



