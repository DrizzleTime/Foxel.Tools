from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from telethon.errors.rpcerrorlist import SessionPasswordNeededError
from telegram_client import TelegramClientManager

router = APIRouter()

@router.websocket("/ws/generate_session")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client = None
    
    async def get_message_from_client(expected_type: str):
        message = await websocket.receive_json()
        if message.get("type") == expected_type:
            return message.get("data")
        raise ValueError(f"Expected message type '{expected_type}', but got '{message.get('type')}'")

    try:
        initial_data = await get_message_from_client("start")
        api_id = initial_data.get("api_id")
        api_hash = initial_data.get("api_hash")

        if not api_id or not api_hash:
            raise ValueError("API ID 和 API Hash 是必需的。")

        client_manager = TelegramClientManager(api_id=api_id, api_hash=api_hash)
        client = client_manager.get_client()

        await client.connect()

        if await client.is_user_authorized():
            session_string = client.session.save()
            await websocket.send_json({"status": "success", "data": session_string})
            return

        await websocket.send_json({"status": "waiting_for_phone"})
        phone = await get_message_from_client("phone")
        
        sent_code = await client.send_code_request(phone)
        
        await websocket.send_json({"status": "waiting_for_code"})
        code = await get_message_from_client("code")

        try:
            await client.sign_in(phone, code, phone_code_hash=sent_code.phone_code_hash)
        except SessionPasswordNeededError:
            await websocket.send_json({"status": "waiting_for_password"})
            password = await get_message_from_client("password")
            await client.sign_in(password=password)

        session_string = client.session.save()
        await websocket.send_json({"status": "success", "data": session_string})

    except (WebSocketDisconnect, ConnectionError):
        print("客户端连接断开")
    except Exception as e:
        print(f"发生错误: {e}")
        await websocket.send_json({"status": "error", "data": str(e)})
    finally:
        if client and client.is_connected():
            await client.disconnect()
        await websocket.close()