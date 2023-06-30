from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func
# from sqlalchemy.sql.functions import func
from .. import models, schemas, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/events",
    tags=['Events']
)

@router.get("/", response_model=List[schemas.EventOut])
def get_events(db: Session = Depends(get_db), current_user: UUID = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    events = db.query(models.Event).filter(models.Event.name.contains(search)).limit(limit).offset(skip).all()
    return events


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.EventOut)
def create_events(event: schemas.EventBase, db: Session = Depends(get_db), current_user: UUID = Depends(oauth2.get_current_user)):
    new_event = models.Event(owner_id=current_user.id, **event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


@router.put("/{id}", response_model=schemas.EventOut)
def update_event(id: UUID, updated_event: schemas.EventBase, db: Session = Depends(get_db), current_user: UUID = Depends(oauth2.get_current_user)):
    event_query = db.query(models.Event).filter(models.Event.id == id)

    event = event_query.first()

    if event == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"event with id: {id} does not exist")

    if event.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    event_query.update(updated_event.dict(), synchronize_session=False)

    db.commit()

    return event_query.first()