import psycopg2

db_conn = psycopg2.connect(user='postgres',
                           password='1242241к',
                           host='localhost',
                           port=5432,
                           database='realestatedb')

cursor = db_conn.cursor()
new_records = [
    ('value1', None, None, '289437744'),
    ('value2', None, None, '289417744'),
    ('value3', None, None, '189417744')
]
insert_query = f"""UPDATE Listings SET seller_name = %s,
		   description = %s,
		   price = %s
WHERE listing_id = %s
RETURNING *"""

cursor.execute(insert_query, new_records[0])
db_conn.commit()

updated_rows = cursor.fetchall()
d = 0
