from fastapi import FastAPI, Depends, APIRouter 
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated


from schemas.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user
