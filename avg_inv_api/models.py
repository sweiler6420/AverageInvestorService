from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIME, DATE, TIMESTAMP, NUMERIC, VARCHAR, INT
from enum import Enum
from database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ =  {'schema' : 'avg_inv'}

    user_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('gen_random_uuid()'))
    username = Column(String, nullable = False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Stocks(Base):
    __tablename__ = "stocks"
    __table_args__ =  {'schema' : 'avg_inv'}

    stock_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('gen_random_uuid()'))
    ticker_symbol = Column(VARCHAR(length=5), nullable = False, unique=True)
    company = Column(VARCHAR(length=150), nullable=False, unique=True)
    market = Column(VARCHAR(length=150), nullable=False)
    isin = Column(VARCHAR(length=12), nullable=False)

class StockData(Base):
    __tablename__ = "stock_data"
    __table_args__ =  {'schema' : 'avg_inv'}

    stock_id = Column(UUID(as_uuid=True), ForeignKey("avg_inv.stocks.stock_id"), primary_key=True, nullable=False)
    date = Column(DATE, nullable = False)
    time = Column(TIME, nullable=False)
    open_price = Column(NUMERIC(precision=8,scale=2), nullable=False)
    high_price = Column(NUMERIC(precision=8,scale=2), nullable=False)
    low_price = Column(NUMERIC(precision=8,scale=2), nullable=False)
    close_price = Column(NUMERIC(precision=8,scale=2), nullable=False)
    volume = Column(INT, nullable=False)

    owner = relationship("Stocks")