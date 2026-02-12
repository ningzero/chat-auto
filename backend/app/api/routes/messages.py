from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
from ..core.database import get_db
from ..models.models import User, Message
from ..models.schemas import MessageCreate, MessageResponse

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("", response_model=List[MessageResponse])
async def get_messages(
    room_id: str = "general",
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """获取聊天消息"""
    result = await db.execute(
        select(Message)
        .where(Message.room_id == room_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    return list(reversed(messages))


@router.post("", response_model=MessageResponse)
async def create_message(
    msg: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建消息"""
    # 简化：这里暂时用用户ID=1
    message = Message(
        content=msg.content,
        author_id=1,
        room_id=msg.room_id,
        is_command=msg.is_command,
        created_at=datetime.utcnow()
    )

    # 分析是否是命令
    if msg.content.startswith("/"):
        message.is_command = 1

    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message
