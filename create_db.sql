CREATE TABLE IF NOT EXISTS Cities (
  city_id SERIAL PRIMARY KEY,
  city_name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Sellers (
  seller_name VARCHAR(255) PRIMARY KEY,
  seller_type VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Websites (
  website_id SERIAL PRIMARY KEY,
  website_name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Listing_Type (
  listing_type_id SERIAL PRIMARY KEY,
  listing_type_name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Address (
 address_id SERIAL PRIMARY KEY,
 full_address VARCHAR(255),
 city_id INTEGER REFERENCES Cities(city_id),
 latitude FLOAT,
 longitude FLOAT
);

CREATE TABLE IF NOT EXISTS Address_Match (
 website_address VARCHAR(255) PRIMARY KEY,
 real_address_id INTEGER REFERENCES Address(address_id)
);

CREATE TABLE IF NOT EXISTS House (
 address_id INTEGER PRIMARY KEY REFERENCES Address(address_id),
 max_floor INT,
 house_serie VARCHAR(255),
 passenger_elevator_count INT,
 freight_elevator_count INT,
 parking_type VARCHAR(255),
 entrance_count INT,
 is_derelicted VARCHAR(255),
 house_type VARCHAR(255),
 gas_supply_type VARCHAR(255),
 is_chute VARCHAR(255),
 concierge BOOLEAN,
 end_build_year INT,
 уard_data VARCHAR(255),
 flooring_type VARCHAR(255),
 house_status VARCHAR(255),
 residential_complex_name VARCHAR(255),
apartments_number INT
);


CREATE TABLE IF NOT EXISTS Listings_Static_Features (
 listings_static_features_id VARCHAR(255) PRIMARY KEY,
 listing_type_id INTEGER REFERENCES Listing_Type(listing_type_id),
 address_id INTEGER REFERENCES Address(address_id),
 room_count INTEGER,
 rooms_type VARCHAR(255),
 property_type VARCHAR(255),
 total_area FLOAT,
 living_area FLOAT,
 kitchen_area FLOAT,
 apartment_floor INT,
 ceiling_height FLOAT,
 window_view VARCHAR(255),
 renovation VARCHAR(255),
 heating_type VARCHAR(255),
 combined_bathroom_count INT,
 separate_bathroom_count INT,
 loggia_count INT,
 balcony_count INT,
 decoration_finishing_type VARCHAR(255),
 furniture VARCHAR(255),
 technique VARCHAR(255),
 heated_floors VARCHAR(255),
 years_owned VARCHAR(255),
 owners_count INT,
 minor_owners BOOLEAN,
 registered_minors BOOLEAN,
 redevelopment BOOLEAN,
 appearing_date DATE DEFAULT CURRENT_TIMESTAMP,
 desapear_date DATE
);

CREATE TABLE IF NOT EXISTS Listings (
 listing_id VARCHAR(255) PRIMARY KEY REFERENCES Listings_Static_Features(listings_static_features_id),
 seller_name VARCHAR(255) REFERENCES Sellers(seller_name),
 description TEXT,
 price FLOAT,
 online_view BOOLEAN,
 negotiation BOOLEAN
);

CREATE TABLE IF NOT EXISTS Listings_Sale (
 listings_sale_id VARCHAR(255) PRIMARY KEY REFERENCES Listings(listing_id),
 conditions VARCHAR(255),
 is_mortgage_available BOOLEAN
);

CREATE TABLE IF NOT EXISTS Listings_Rent (
 listings_rent_id VARCHAR(255) PRIMARY KEY REFERENCES Listings(listing_id),
 rental_period VARCHAR(255),
 is_communal_payments_included BOOLEAN,
 pledge INTEGER,
 commission INTEGER,
 prepayment INTEGER
 --Добавить поля
);

CREATE TABLE IF NOT EXISTS Websites_Listings_Map (
 map_id SERIAL PRIMARY KEY,
 listing_id VARCHAR(255) REFERENCES Listings(listing_id),
 website_id INTEGER REFERENCES Websites(website_id),
 link_url TEXT
);

CREATE TABLE IF NOT EXISTS Listing_Images (
  image_id SERIAL PRIMARY KEY,
  listing_id VARCHAR(255) REFERENCES Listings(listing_id),
  image_path TEXT
);

CREATE TABLE IF NOT EXISTS House_Changes (
 change_id SERIAL PRIMARY KEY,
 address_id INTEGER REFERENCES House(address_id),
 end_build_year INT,
 house_status VARCHAR(255),
 is_derelicted VARCHAR(255),
 change_data DATE
);

CREATE TABLE IF NOT EXISTS Listings_Changes (
 change_id SERIAL PRIMARY KEY,
 listing_id VARCHAR(255) REFERENCES Listings(listing_id),
 change_timestamp TIMESTAMP DEFAULT current_timestamp,
 seller_name VARCHAR(255) REFERENCES Sellers(seller_name),
 description TEXT,
 price FLOAT,
 online_view BOOLEAN,
 negotiation BOOLEAN,
 change_data DATE
);

CREATE TABLE IF NOT EXISTS Listings_Sale_Changes (
 change_id SERIAL PRIMARY KEY,
 listings_sale_id VARCHAR(255) REFERENCES Listings(listing_id),
 change_timestamp TIMESTAMP DEFAULT current_timestamp,
 conditions VARCHAR(255),
 is_mortgage_available BOOLEAN
);

CREATE TABLE IF NOT EXISTS Listings_Rent_Changes (
 change_id SERIAL PRIMARY KEY,
 listings_rent_id VARCHAR(255) REFERENCES Listings(listing_id),
 change_timestamp TIMESTAMP DEFAULT current_timestamp,
 is_communal_payments_included BOOLEAN,
 pledge INTEGER,
 commission INTEGER,
 prepayment INTEGER
);