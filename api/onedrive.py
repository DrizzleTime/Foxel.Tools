import asyncio
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
import httpx

router = APIRouter()

state_storage = {}

@router.websocket("/ws/onedrive_token")
async def onedrive_token_ws(websocket: WebSocket):
    await websocket.accept()
    state = str(uuid.uuid4())
    
    try:
        message = await websocket.receive_json()
        if message.get("type") == "start":
            client_id = message.get("data", {}).get("client_id")
            client_secret = message.get("data", {}).get("client_secret")

            if not client_id or not client_secret:
                await websocket.send_json({"status": "error", "data": "Client ID and Client Secret are required."})
                return
            
            state_storage[state] = {
                "websocket": websocket,
                "client_id": client_id,
                "client_secret": client_secret
            }

            redirect_uri = "https://tools.foxel.cc/api/onedrive/callback"
            auth_url = (
                "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
                f"?client_id={client_id}"
                "&response_type=code"
                f"&redirect_uri={redirect_uri}"
                "&response_mode=query"
                "&scope=offline_access files.readwrite.all"
                f"&state={state}"
            )
            await websocket.send_json({"status": "waiting_for_auth", "data": auth_url})
            
            # 等待回调处理
            while state in state_storage:
                await asyncio.sleep(1)

    except WebSocketDisconnect:
        print(f"WebSocket for state {state} disconnected.")
    except Exception as e:
        print(f"Error in onedrive_token_ws: {e}")
        await websocket.send_json({"status": "error", "data": str(e)})
    finally:
        if state in state_storage:
            del state_storage[state]
        await websocket.close()

@router.get("/onedrive/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    
    if not state or state not in state_storage:
        return HTMLResponse(content="<h1>错误：无效的状态码</h1>", status_code=400)

    storage_entry = state_storage.get(state, {})
    websocket = storage_entry.get("websocket")
    client_id = storage_entry.get("client_id")
    client_secret = storage_entry.get("client_secret")

    if not websocket or not client_id or not client_secret:
        return HTMLResponse(content="<h1>错误：会话已过期或无效</h1>", status_code=400)

    try:
        redirect_uri = "https://tools.foxel.cc/api/onedrive/callback"

        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        payload = {
            "client_id": client_id,
            "scope": "offline_access files.readwrite.all",
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "client_secret": client_secret,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=payload)
        response_data = response.json()

        if "refresh_token" in response_data:
            refresh_token = response_data["refresh_token"]
            await websocket.send_json({"status": "success", "data": refresh_token})
            return HTMLResponse(content="<h1>授权成功！</h1><p>您现在可以关闭此页面。</p>")
        else:
            error_description = response_data.get("error_description", "未知错误")
            await websocket.send_json({"status": "error", "data": error_description})
            return HTMLResponse(content=f"<h1>错误</h1><p>{error_description}</p>", status_code=400)

    except Exception as e:
        await websocket.send_json({"status": "error", "data": str(e)})
        return HTMLResponse(content=f"<h1>发生内部错误</h1><p>{e}</p>", status_code=500)
    finally:
        if state in state_storage:
            del state_storage[state]