import uuid

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Product(Base):
    __tablename__ = 'product'
    
    articlenumber = Column(Integer, primary_key=True)
    articlename = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    
    __table_args__ = (
        CheckConstraint('price == ROUND(price, 2)', name='check_price'),
    )

class Customer(Base):
    __tablename__ = 'customer'
    customer_id = Column(String, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('first_name', 'last_name', 'email', name='unique_customer'),
    )
    
    def __init__(self, first_name, last_name, email, birthdate):
        self.customer_id = str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.birthdate = birthdate

class Shop(Base):
    __tablename__ = 'shop'
    
    shopnumber = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)

class OrderHeader(Base):
    __tablename__ = 'order_header'

    order_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey('customer.customer_id'), nullable=False)
    manufacturer = Column(String, nullable=False)
    manufactur_place = Column(String, nullable=False)
    shopnumber = Column(Integer, ForeignKey('shop.shopnumber'), nullable=False)
    date = Column(Date, nullable=False)
    
    customer = relationship("Customer", back_populates="orders")
    shop = relationship("Shop", back_populates="orders")
    def __init__(self, customer_id, manufacturer, manufactur_place, shopnumber, date):
        self.order_id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.manufacturer = manufacturer
        self.manufactur_place = manufactur_place
        self.shopnumber = shopnumber
        self.date = date
class OrderItem(Base):
    __tablename__ = 'order_item'    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey('order_header.order_id'), nullable=False)
    articlenumber = Column(Integer, ForeignKey('product.articlenumber'), nullable=False)
    articlename = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    order_date = Column(Date, nullable=False)
    
    order = relationship("OrderHeader", back_populates="items")
    product = relationship("Product")

    __table_args__ = (
        CheckConstraint('price == ROUND(price, 2)', name='check_order_item_price'),
    )
    def __init__(self, order_id, articlenumber, articlename, quantity, price, currency, order_date):
        self.id = str(uuid.uuid4())
        self.order_id = order_id
        self.articlenumber = articlenumber
        self.articlename = articlename
        self.quantity = quantity
        self.price = price
        self.currency = currency
        self.order_date = order_date



Customer.orders = relationship("OrderHeader", order_by=OrderHeader.order_id, back_populates="customer")
Shop.orders = relationship("OrderHeader", order_by=OrderHeader.order_id, back_populates="shop")
OrderHeader.items = relationship("OrderItem", order_by=OrderItem.id, back_populates="order")
