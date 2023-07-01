import sys
sys.path.append("..")

from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import models, schemas, utils, oauth2
from database import get_db
from uuid import UUID

router = APIRouter(
    prefix="/stock_data",
    tags=['Stock_data']
)

@router.get('/', response_model=List[schemas.StockData])
def get_user(db: Session = Depends(get_db), limit: int = 108, offset: int = 0, search: Optional[str] = ""):
    print(search, limit, offset)
    stock_data = db.query(models.StockData).join(models.Stocks, models.StockData.stock_id == models.Stocks.stock_id, isouter=False).filter(models.Stocks.ticker_symbol.contains(func.lower(search))).order_by(models.StockData.date.desc(), models.StockData.time.desc()).limit(limit).offset(offset).all()

    if not stock_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock with id: {search} does not exist")

    return stock_data