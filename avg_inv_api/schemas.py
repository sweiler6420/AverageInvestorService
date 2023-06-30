from pydantic import BaseModel, EmailStr
from datetime import datetime, date, time
from typing import Optional
from uuid import UUID

class UserOut(BaseModel):
    user_id: UUID
    email: EmailStr
    username: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[UUID] = None

class Stocks(BaseModel):
    stock_id:  UUID
    ticker_symbol: str
    company: str
    market: str
    isin: str

    class Config:
        orm_mode = True

class StockData(BaseModel):
    stock_id:  UUID
    date: date
    time: time
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int