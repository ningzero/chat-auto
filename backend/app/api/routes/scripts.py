from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.models.schemas import ScriptResponse, ScriptTaskResponse
from app.services.script_service import script_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/scripts", tags=["scripts"])


class CommandInfo(BaseModel):
    name: str
    description: str


# 内置命令定义
BUILTIN_COMMANDS = [
    CommandInfo(name="/list", description="List all available scripts"),
    CommandInfo(name="/status", description="Check task status: /status <task_id>"),
]


@router.get("/commands", response_model=List[CommandInfo])
async def list_commands(db: AsyncSession = Depends(get_db)):
    """获取所有可用命令（内置命令 + 脚本命令）"""
    commands = BUILTIN_COMMANDS.copy()
    scripts = await script_service.get_all_scripts(db)
    for script in scripts:
        if script.command_pattern not in [cmd.name for cmd in commands]:
            commands.append(
                CommandInfo(
                    name=script.command_pattern,
                    description=script.description or f"Run {script.name} script"
                )
            )
    return commands


@router.get("", response_model=List[ScriptResponse])
async def list_scripts(db: AsyncSession = Depends(get_db)):
    """获取所有可用脚本"""
    scripts = await script_service.get_all_scripts(db)
    return scripts


@router.post("/register", response_model=ScriptResponse)
async def register_script(
    name: str,
    path: str,
    description: str = None,
    command_pattern: str = None,
    db: AsyncSession = Depends(get_db)
):
    """注册新脚本"""
    script = await script_service.register_script(
        db=db,
        name=name,
        path=path,
        description=description,
        command_pattern=command_pattern
    )
    return script


@router.get("/tasks/{task_id}", response_model=ScriptTaskResponse)
async def get_task_status(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取脚本任务状态"""
    task = await script_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
