from pydantic import BaseModel


class Sellers(BaseModel):
    name: str


class Address(BaseModel):
    name: str


class House(BaseModel):
    name: str


class Listings_Static_Features(BaseModel):
    name: str


class Listings(BaseModel):
    name: str


class Listings_Sale(BaseModel):
    name: str


class Listings_Rent(BaseModel):
    name: str

