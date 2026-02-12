import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.core.database import get_db
from app.models.models import User, Message, ScriptTask
from app.services.script_service import script_service

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        return len(self.active_connections[room_id]) - 1

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)

    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)
            for conn in disconnected:
                self.active_connections[room_id].remove(conn)


manager = ConnectionManager()


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    db: AsyncSession = Depends(get_db)
):
    # 使用固定用户
    username = "user"
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            username=username,
            nickname="User",
            is_admin=1
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    await manager.connect(websocket, room_id)

    # 发送用户加入消息
    await manager.broadcast({
        "type": "user_join",
        "data": {
            "user": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    }, room_id)

    try:
        while True:
            data = await websocket.receive_json()

            msg_type = data.get("type")
            msg_content = data.get("content", "")
            token = data.get("token")

            # 保存消息到数据库
            message = Message(
                content=msg_content,
                author_id=user.id,
                room_id=room_id,
                is_command=int(msg_content.startswith("/")),
                created_at=datetime.utcnow()
            )
            db.add(message)
            await db.commit()
            await db.refresh(message)

            # 处理斜杠命令
            if msg_content.startswith("/"):
                parts = msg_content.strip().split()

                # /list - 列出可用脚本
                if parts[0] == "/list":
                    scripts = await script_service.get_all_scripts(db)
                    scripts_list = [
                        {
                            "name": s.name,
                            "description": s.description,
                            "command": s.command_pattern
                        } for s in scripts
                    ]
                    result_data = {
                        "type": "list_scripts",
                        "scripts": scripts_list
                    }
                    message.command_result = json.dumps(result_data)
                    db.add(message)
                    await db.commit()
                    await db.refresh(message)
                    await manager.broadcast({
                        "type": "command_result",
                        "data": {
                            "command": msg_content,
                            "result": result_data,
                        },
                        "user_id": user.id
                    }, room_id)
                    continue

                # /status <task_id> - 查看任务状态
                elif parts[0] == "/status" and len(parts) > 1:
                    try:
                        task_id = int(parts[1])
                        task = await script_service.get_task(db, task_id)
                        if task:
                            result_data = {
                                "type": "task_status",
                                "task": {
                                    "id": task.id,
                                    "status": task.status,
                                    "exit_code": task.exit_code,
                                    "output": task.output,
                                    "error": task.error
                                }
                            }
                            message.command_result = json.dumps(result_data)
                            db.add(message)
                            await db.commit()
                            await db.refresh(message)
                            await manager.broadcast({
                                "type": "command_result",
                                "data": {
                                    "command": msg_content,
                                    "result": result_data,
                                },
                                "user_id": user.id
                            }, room_id)
                        else:
                            error_data = f"Task {task_id} not found"
                            message.error_message = error_data
                            db.add(message)
                            await db.commit()
                            await db.refresh(message)
                            await manager.broadcast({
                                "type": "error",
                                "data": {
                                    "command": msg_content,
                                    "message": error_data
                                }
                            }, room_id)
                    except ValueError:
                        error_data = "Invalid task ID"
                        message.error_message = error_data
                        db.add(message)
                        await db.commit()
                        await db.refresh(message)
                        await manager.broadcast({
                            "type": "error",
                            "data": {
                                "command": msg_content,
                                "message": error_data
                            }
                        }, room_id)
                    continue

                # 尝试匹配脚本命令
                command_pattern = msg_content.split()[0] if msg_content.split() else ""
                if command_pattern:
                    script = await script_service.get_script_by_pattern(db, command_pattern)
                    if script:
                        # 执行脚本
                        task = await script_service.execute_script(db, script, user.id)
                        await manager.broadcast({
                            "type": "command_result",
                            "data": {
                                "command": msg_content,
                                "result": {
                                    "type": "script_started",
                                    "message": f"Script '{script.name}' started",
                                    "task_id": task.id,
                                    "script": script.name
                                }
                            },
                            "user_id": user.id
                        }, room_id)

                        # 执行完成后发送结果并保存
                        while task and task.status in ("pending", "running"):
                            await asyncio.sleep(0.5)
                            task = await script_service.get_task(db, task.id)

                        if task:
                            result_data = {
                                "type": "script_completed",
                                "task_id": task.id,
                                "script": script.name,
                                "status": task.status,
                                "exit_code": task.exit_code,
                                "output": task.output,
                                "error": task.error
                            }
                            message.command_result = json.dumps(result_data)
                            db.add(message)
                            await db.commit()
                            await db.refresh(message)
                            await manager.broadcast({
                                "type": "command_result",
                                "data": {
                                    "command": msg_content,
                                    "result": result_data,
                                },
                                "user_id": user.id
                            }, room_id)
                        continue

                # 未知命令
                error_data = f"Unknown command: {command_pattern}. Use /list to see available commands."
                message.error_message = error_data
                db.add(message)
                await db.commit()
                await db.refresh(message)
                await manager.broadcast({
                    "type": "error",
                    "data": {
                        "command": msg_content,
                        "message": error_data
                    }
                }, room_id)
                continue

            # 广播普通消息（非命令）
            await manager.broadcast({
                "type": "message",
                "data": {
                    "id": message.id,
                    "content": message.content,
                    "is_command": message.is_command,
                    "author_id": message.author_id,
                    "room_id": message.room_id,
                    "command_result": message.command_result,
                    "error_message": message.error_message,
                    "created_at": message.created_at.isoformat(),
                    "author": {
                        "id": user.id,
                        "username": user.username,
                        "nickname": user.nickname,
                    }
                }
            }, room_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast({
            "type": "user_leave",
            "data": {
                "user_id": user.id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }, room_id)
