from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from routes.sample_frontend import router
from routes.history import router as history_router 
from routes.mcq import router as mcq_router 
from auth.login import router as login_router    


app = FastAPI()

app.include_router(router) 
app.include_router(history_router)
app.include_router(login_router)
app.include_router(mcq_router)

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
