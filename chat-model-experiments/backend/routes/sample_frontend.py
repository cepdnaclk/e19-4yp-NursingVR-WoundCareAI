from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer  
from typing import Annotated
from fastapi import Depends

from auth.auth import get_current_active_user

router = APIRouter()

@router.get("/hello")
async def sayHello():
    return {"message": "Hello from the sample frontend!"}

@router.get("/protected")
async def protected_route(current_user: Annotated[str, Depends(get_current_active_user)]):   
    print(current_user)
    return {"message": "This is a protected route, you have access!"}   


# @router.get('/')
# async def get_html():
#     return HTMLResponse(html)  

@router.get('/')
async def get_html_mcq():
    return HTMLResponse(html_mcq)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat 1.0</title>
    </head> 
    <body>
        <h1>WebSocket Chat</h1>

            <input type="text" id="messageText" autocomplete="off"/>
            <button id="recordBtn" type="button">Record</button>
            <button id="stopBtn" type="button" disabled>Stop</button>

        <ul id='messages'>
        </ul>
        <script src="static/script.js"></script>

    </body>
</html>
"""

html_mcq = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat 1.0</title>
    </head> 
    <body>
        <h1>WebSocket Chat</h1>
            <button id="sendBtn" type="button">Send Q&A</button>
        <script src="static/mcq_script.js"></script>
    </body>
</html>
"""