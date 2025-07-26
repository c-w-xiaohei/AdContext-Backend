from services.websocket import websocket_manager
from schemas.websocket import OperationResultPayload
import uuid

async def request_blockchain_data(data_id:str):
    request_id = str(uuid.uuid4())
    
    await websocket_manager.send_json({
        "type": "REQUEST_DECRYPTION",
        "requestId": request_id,
        "payload": { "dataId": data_id }
    })

    response: OperationResultPayload = await websocket_manager.wait_for_response(request_id)

    if response and response.get("success"):
        plaintext = response.get("data", {}).get("plaintext")
        print(f"[后端] 成功解密数据ID: {data_id}")
        return str(plaintext) # 确保返回的是字符串
    else:
        error_msg = response.get("error", "未知错误") if response else "超时"
        print(f"[后端] 解密数据ID {data_id} 失败: {error_msg}")
        return None