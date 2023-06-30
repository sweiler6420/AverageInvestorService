from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from typing import List, Optional
from ..database import get_db
from uuid import UUID

router = APIRouter(
    prefix="/image",
    tags=['Images']
)

@router.get("/", response_model=List[schemas.ImageOut])
def get_image(db: Session = Depends(get_db), current_user: UUID = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0):
    images = db.query(models.Image).limit(limit).offset(skip).all()

    return images

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ImageOut)
def create_image(image: schemas.ImageBase, db: Session = Depends(get_db), current_user: UUID = Depends(oauth2.get_current_user)):

    # location = f'https://cac-image-data-lake.s3.amazonaws.com/'

    new_image = models.Image(owner_id=current_user.id, **image.dict())
    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return new_image

@router.put("/{id}", response_model=schemas.ImageOut)
def update_location(id: UUID, updated_image: schemas.ImageBase, db: Session = Depends(get_db), current_user: UUID = Depends(oauth2.get_current_user)):
    image_query = db.query(models.Image).filter(models.Image.id == id)

    image = image_query.first()

    if image == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"image with id: {id} does not exist")

    if image.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    image_query.update(updated_image.dict(), synchronize_session=False)

    db.commit()

    return image_query.first()


@router.get("/{id}", response_model=schemas.ImageOut)
def get_image(id: UUID, db: Session = Depends(get_db), current_user: UUID = Depends(oauth2.get_current_user)):
    image = db.query(models.Image).filter(models.Image.id == id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"image with id: {id} does not exist")

    return image