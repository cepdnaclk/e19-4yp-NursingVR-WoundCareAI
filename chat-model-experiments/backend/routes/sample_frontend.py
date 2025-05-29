from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer  
from typing import Annotated
from fastapi import Depends

from auth.auth import get_current_user

router = APIRouter()

@router.get("/hello")
async def sayHello():
    return {"message": "Hello from the sample frontend!"}

@router.get("/protected")
async def protected_route(current_user: Annotated[str, Depends(get_current_user)]):   
    print(current_user)
    return {"message": "This is a protected route, you have access!"}   


@router.get('/')
async def get_html():
    return HTMLResponse(html)  


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat 1.0</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/history");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""