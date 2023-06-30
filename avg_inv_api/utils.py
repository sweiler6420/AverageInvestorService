from passlib.context import CryptContext
from geopy.geocoders import Nominatim

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_coords(street: str, city: str, zip_code: str, state: str):
    app = Nominatim(user_agent="CarsAndCoffee")
    address = f"""{street}, {state}, {city} {zip_code}, United States"""
    location = app.geocode(address).raw
    return location['lat'], location['lon']