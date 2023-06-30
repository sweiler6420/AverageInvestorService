from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import UUID
import boto3

from ..config import settings
from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    # create a token
    # return token

    # Must convert UUID to string since UUID cannot be serialized
    user = str(user.id)

    # Encode user roles if we decide to add roles
    access_token = oauth2.create_access_token(data={"user_id": user})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/url', response_model=schemas.S3SecureUrl)
def s3_secure_url(image_uuid: UUID, current_user: UUID = Depends(oauth2.get_current_user)):

    # Get Boto3 client with access info from env variables
    s3_client = boto3.client(
        's3',
        aws_access_key_id = settings.s3_access_key_id,
        aws_secret_access_key = settings.s3_secret_access_key
    )

    #generate presigned url
    response = s3_client.generate_presigned_post(
        Bucket = 'cac-image-data-lake',
        Key = str(image_uuid),
        ExpiresIn = 60 # in seconds
    )

    # Response holds the presigned url, extract that url and send back
    print(response)

    return response
