import datetime
import os
import time
import pandas as pd
import warnings

import psycopg2


class DataWorker:
    def __init__(self):
        self.data_to_save_queue = []
        self.is_run = True
        self.keys = set()
        self.seller_keys = ['Название продаца', 'Тип продаца']
        self.lisitng_type_keys = ['Тип обьявления']
        self.adress_keys = ['Адресс', 'Город id']
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
            'id',
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
            'Дата публикации'
        ]
        self.listings_keys = [
            'id',
            'Цена',
            'Дата исчезновения',
            'Описание'
        ]
        self.lisitng_sale_keys = [
            'id',
            'Условия сделки',
            'Ипотека'
        ]
        self.lisitng_rent_keys = [
            'id'
        ]
        self.website_listings_map_keys = [
            'Ссылка'
        ]
        self.listings_images_keys = [
            'Путь к картинкам'
        ]
        self.not_changed_keys = ['appearing_date']
        warnings.filterwarnings("ignore")
        self.db_connection = psycopg2.connect(
                                            user="postgres",
                                            password="1242241к",
                                            host="localhost",
                                            port="5432",
                                            database="realestatedb"
                                        )

    def get_id_by_condition(self, talbe, table_id, condition_value, condition_column):
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
                values.append(datetime.date.today())
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
            'seller_name': data['Название продаца'],
            'seller_type': data['Тип продаца'],
        }
        return self.update_or_past(record, 'seller_name', 'Sellers')

    def update_or_past_addres(self, data):
        record = {
            'addres': data['Адресс'],
            'city_id': data['Город id']
        }
        return self.update_or_past(record, 'addres', 'Address')

    def update_or_past_house_features(self, data):
        record = {
            'addres': data['Адресс'],
            'max_floor': data['Этажей в доме'],
            'house_serie': data['Строительная серия'],
            'passenger_elevator_count': data['Пассажирский лифт'],
            'freight_elevator_count': data['Грузовой лифт'],
            'parking_type': data['Парковка'],
            'entrance_count': data['Подъезды'],
            'is_derelicted': data['Аварийность'],
            'house_type': data['Тип дома'],
            'gas_supply_type': data['Газоснабжение'],
            'is_chute': data['Мусоропровод'],
            'end_build_year': data['Год постройки'] if data['Год постройки'] is not None else data['Год сдачи'],
            'flooring_type': data['Тип перекрытий'],
            'house_status': data['Дом'],
            'residential_complex_name': data['Название ЖК'],
        }
        history_keys = ['addres','end_build_year', 'house_status', 'is_derelicted']
        return self.update_or_past(record, 'addres', 'House_Features', history_keys)

    def update_or_past_listings_static_features(self, data):
        record = {
            'listings_static_features_id': data['id'],
            'listing_type_id': data['Тип обьявления id'],
            'addres': data['Адресс'],
            'room_count': data['Число комнат'],
            'property_type': data['Тип жилья'],
            'total_area': data['Общая площадь'],
            'living_area': data['Жилая площадь'],
            'kitchen_area': data['Площадь кухни'],
            'apartment_floor': data['Этаж квартиры'],
            'ceiling_height': data['Высота потолков'],
            'window_view': data['Вид из окон'],
            'renovation': data['Ремонт'],
            'heating_type': data['Отопление'],
            'combined_bathroom_count': data['Совмещенный санузел'],
            'separate_bathroom_count': data['Раздельный санузел'],
            'loggia_count': data['Лоджия'],
            'balcony_count': data['Балкон'],
            'decoration_finishing_type': data['Отделка'],
            'appearing_date': data['Дата публикации'],
            'desapear_date': data['Дата исчезновения']
        }
        return self.update_or_past(record, 'listings_static_features_id', 'Listings_Static_Features')

    def update_or_past_listings(self, data):
        record = {
            'listing_id': data['id'],
            'seller_name': data['Название продаца'],
            'description': data['Описание'],
            'price': data['Цена'],
        }
        history_keys = ['listing_id', 'seller_name', 'description', 'price']
        return self.update_or_past(record, 'listing_id', 'Listings', history_keys)

    def update_or_past_listings_sale(self, data):
        record = {
            'listings_sale_id': data['id'],
            'conditions': data['Условия сделки'],
            'is_mortgage_available': data['Ипотека'],
        }
        history_keys = ['listings_sale_id', 'conditions', 'is_mortgage_available']
        return self.update_or_past(record, 'listings_sale_id', 'Listings_Sale', history_keys)

    def update_or_past_listings_rent(self, data):
        record = {
            'listings_rent_id': data['id']
        }
        history_keys = ['listings_rent_id']
        return self.update_or_past(record, 'listings_rent_id', 'Listings_Rent', history_keys)

    def update_or_past_websites_listings_map(self, data):
        record = {
            'listing_id': data['id'],
            'website_id': data['Сайт id'],
            'link_url': data['Ссылка'],
        }
        self.instert_to_db(record, 'Websites_Listings_Map')

    def update_or_past_listing_images(self, data):
        record = {
            'listing_id': data['id'],
            'image_path': data['Путь к картинкам']
        }
        self.instert_to_db(record, 'Listing_Images')

    def get_website_id(self, website_name):
        return self.get_id_by_condition('Websites', 'website_id', website_name, 'website_name')

    def get_city_id(self, city):
        return self.get_id_by_condition('Cities','city_id',  city, 'city_name')

    def get_listing_type_id(self, listing_type):
        return self.get_id_by_condition('Listing_Type', 'listing_type_id', listing_type, 'listing_type_name')

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
            # print(e)
            # print(field, data[field])
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
        if data['Тип обьявления id'] == 2:
            possible_keys |= set(self.lisitng_rent_keys)
        else:
            possible_keys |= set(self.lisitng_sale_keys)

        for key in possible_keys:
            if key not in data.keys():
                data[key] = None

    def type_convert(self, data):
        #data['Цена'] = int(data['Цена'])
        data['Цена'] = DataWorker.type_convert_if_possible(data, 'Цена', int)
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

    def run_db(self):
        while self.is_run:
            if len(self.data_to_save_queue) > 0:
                data = self.data_to_save_queue.pop(0)
                self.data_dict_flatten(data)
                self.add_none_fields(data)
                self.type_convert(data)
                if data['Название продаца'] is not None:
                    self.update_or_past_seller(data)
                self.update_or_past_addres(data)
                self.update_or_past_house_features(data)
                self.update_or_past_listings_static_features(data)
                is_new = self.update_or_past_listings(data)
                if data['Тип обьявления id'] == 1:
                    self.update_or_past_listings_sale(data)
                else:
                    self.update_or_past_listings_rent(data)

                if is_new:
                    self.update_or_past_websites_listings_map(data)
                    self.update_or_past_listing_images(data)
            else:
                time.sleep(5)

    def run_csv(self):
        if os.path.exists('offers.csv'):
            os.remove('offers.csv')
        open('offers.csv', 'w').close()

        while self.is_run:
            if len(self.data_to_save_queue) > 0:
                data = self.data_to_save_queue.pop(0)
                self.data_dict_flatten(data)
                self.add_none_fields(data)
                self.type_convert(data)
                try:
                    df = pd.read_csv('offers.csv')
                except:
                    df = pd.DataFrame()
                df = pd.concat([df, pd.DataFrame([pd.Series(data)])], ignore_index=True)
                df.to_csv('offers.csv', mode='w', index=False)
            else:
                time.sleep(5)

    def __del__(self):
        self.db_connection.close()



