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


@router.get('/')
async def get_html():
    return HTMLResponse(html)  

@router.get('/mcq')
async def get_html_mcq():
    return HTMLResponse(html_mcq)

@router.get('/evaluation')
async def get_html_evaluation():
    return HTMLResponse(html_evaluation)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat 1.0</title>
    </head> 
    <body>
        <h1>WebSocket Chat 2</h1>

        <h2>Audio Chat Agent</h2>
        <input type="text" id="messageText" autocomplete="off"/>
        <button id="recordBtn" type="button">Record</button>
        <button id="stopBtn" type="button" disabled>Stop</button>

        <h2>MCQ Agent</h2>
        <button id="sendBtn" type="button">Send MCQ Test</button>

        <h2>Agent 2</h2>
        <button id="recordAgent2Btn" type="button">Record Agent2</button>
        <button id="stopAgent2Btn" type="button" disabled>Stop Agent2</button>

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

html_evaluation = """
<!DOCTYPE html> 
<html>
    <head>
        <title>Evaluation</title>
    </head> 
    <body>
        <h1>Evaluation</h1>
        <button id="evaluateBtn" type="button">Evaluate Patient Conversation</button>
        <script src="static/evaluation_script.js"></script>
    </body>
</html>
"""