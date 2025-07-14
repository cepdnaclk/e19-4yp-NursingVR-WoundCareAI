from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from starlette.requests import Request

from routes.sample_frontend import router
from routes.history import router as history_router 
from routes.mcq import router as mcq_router 
from routes.stuff_nurse import router as agent2_router 
from routes.logs import router as logs_router
from routes.evaluation import router as evaluation_router
from auth.login import router as login_router    


app = FastAPI()

app.include_router(router) 
app.include_router(history_router)
app.include_router(agent2_router)
app.include_router(logs_router)
app.include_router(evaluation_router)
app.include_router(login_router)
app.include_router(mcq_router)


from fastapi.staticfiles import StaticFiles

class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, request: Request):
        response = await super().get_response(path, request)
        # Only for .js files (you can extend this to .css, etc.)
        if path.endswith(".js"):
            response.headers["Cache-Control"] = "no-store"
        return response


app.mount("/static", StaticFiles(directory="static"), name="static")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
