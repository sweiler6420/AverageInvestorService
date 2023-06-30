import sys
sys.path.append("..")

from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
import models, schemas, utils, oauth2
from database import get_db
from uuid import UUID

router = APIRouter(
    prefix="/stocks",
    tags=['Stocks']
)

@router.get('/{id}', response_model=schemas.Stocks)
def get_user(stock_id: UUID, db: Session = Depends(get_db), current_user: UUID = Depends(oauth2.get_current_user)):
    stock = db.query(models.Stocks).filter(models.Stocks.stock_id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock with id: {stock_id} does not exist")

    return stock