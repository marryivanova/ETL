from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, Text

Base = declarative_base()


class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    image = Column(Text)
    price = Column(Float, nullable=False)
    description = Column(Text)
    brand = Column(String(100))
    model = Column(String(100))
    color = Column(String(50), nullable=True)
    category = Column(String(100))
    discount = Column(Integer, nullable=True)
    popular = Column(Boolean, nullable=True)
    on_sale = Column(Boolean, nullable=True)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(JSON, nullable=False)
    address = Column(JSON, nullable=False)
    phone = Column(String(50))


class MostExpensive(Base):
    __tablename__ = 'most_expensive'

    id = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)


class OdsUser(Base):
    __tablename__ = 'ods_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    firstname = Column(String(100))
    lastname = Column(String(100))
    lat = Column(Float)
    long = Column(Float)
    street_number = Column(String(50))
    street = Column(String(255))
    zipcode = Column(String(20))
    city = Column(String(100))


TABLES = {
    "products": ProductDB,
    "users": UserDB,
    "most_expensive": MostExpensive,
    "ods_users": OdsUser
}