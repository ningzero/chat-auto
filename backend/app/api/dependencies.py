from fastapi import Depends, HTTPException, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..core.config import settings

security = HTTPBearer()


async def get_current_user_ws(
    websocket: WebSocket,
    token: str | None = None
):
    """WebSocket 用户认证"""
    if token:
        # 简化版：直接使用 token 作为 username
        username = token
        return {"username": username, "user_id": hash(username) % 1000000}

    username = f"user_{id(websocket) % 1000}"
    return {"username": username, "user_id": hash(username) % 1000000}
