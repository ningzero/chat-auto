from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    nickname = Column(String(100))
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="author")
    script_tasks = relationship("ScriptTask", back_populates="user")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    is_command = Column(Integer, default=0)
    author_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(String(50), default="general")
    command_result = Column(Text, nullable=True)  # 命令执行结果
    error_message = Column(Text, nullable=True)   # 命令执行错误
    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="messages")


class Script(Base):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    path = Column(String(255), nullable=False)
    command_pattern = Column(String(100))  # 触发的斜杠命令，如 "/deploy"
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScriptTask(Base):
    __tablename__ = "script_tasks"

    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    exit_code = Column(Integer)
    output = Column(Text)
    error = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    script = relationship("Script")
    user = relationship("User", back_populates="script_tasks")
