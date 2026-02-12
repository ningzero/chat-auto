from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# 用户相关
class UserCreate(BaseModel):
    username: str
    nickname: Optional[str] = None
    is_admin: Optional[int] = 0


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    is_admin: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str


# 消息相关
class MessageCreate(BaseModel):
    content: str
    room_id: Optional[str] = "general"
    is_command: Optional[int] = 0


class MessageResponse(BaseModel):
    id: int
    content: str
    is_command: int
    author_id: int
    room_id: str
    created_at: datetime
    author: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# 脚本相关
class ScriptCreate(BaseModel):
    name: str
    description: Optional[str] = None
    path: str
    command_pattern: str


class ScriptResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    path: str
    command_pattern: str
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


# 脚本任务相关
class ScriptTaskCreate(BaseModel):
    script_id: int
    user_id: int


class ScriptTaskResponse(BaseModel):
    id: int
    script_id: int
    user_id: int
    status: str
    exit_code: Optional[int] = None
    output: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# WebSocket 消息
class WSMessage(BaseModel):
    type: str  # message, command, script_output, user_join, user_leave
    data: dict


class WSCommandRequest(BaseModel):
    command: str
    args: Optional[dict] = None
