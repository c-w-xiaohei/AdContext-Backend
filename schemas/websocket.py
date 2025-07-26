# protocol_types.py

from typing import TypedDict, Literal, Optional, List

# This file defines the WebSocket message protocols between the server and client,
# based on the TypeScript type definitions.

# =============================================
# 0. Data Structures
# =============================================

class Category(TypedDict):
    name: str
    color: str

class AppMemory(TypedDict):
    """
    Represents a memory object, which is the core data structure for user content.
    """
    id: str
    text: str
    time: str
    categories: List[Category]
    privacy: str

# =============================================
# 1. 从服务器发往客户端的消息 (Server -> Client)
# =============================================

class RequestOnchainStoragePayload(TypedDict):
    """
    Payload for requesting on-chain storage.
    The data must be a string.
    """
    dataToStore: str

class RequestOnchainStorage(TypedDict):
    """
    Server requests the client to store data on-chain.
    The data will be encrypted by the client before storage.
    """
    type: Literal['REQUEST_ONCHAIN_STORAGE']
    requestId: str
    payload: RequestOnchainStoragePayload

class RequestDecryptionPayload(TypedDict):
    """
    Payload for requesting decryption of on-chain data.
    """
    dataId: str # The unique ID for the data on the chain

class RequestDecryption(TypedDict):
    """
    Server requests the client to decrypt data from the chain.
    """
    type: Literal['REQUEST_DECRYPTION']
    requestId: str
    payload: RequestDecryptionPayload

# Union type for all possible messages from server to client
ServerMessage = RequestOnchainStorage | RequestDecryption


# =============================================
# 2. 从客户端发往服务器的消息 (Client -> Server)
# =============================================

class OperationResultPayload(TypedDict):
    """
    Payload for the result of a client-side operation.
    """
    success: bool
    data: Optional[str] # On success, e.g., txHash or decrypted plaintext
    error: Optional[str] # On failure, the error message

class OperationResult(TypedDict):
    """
    Client responds to a server request, indicating the result of the operation.
    """
    type: Literal['OPERATION_RESULT']
    requestId: str # Must match the requestId from the server's request
    payload: OperationResultPayload

# Union type for all possible messages from client to server
ClientMessage = OperationResult