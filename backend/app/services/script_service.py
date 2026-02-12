import asyncio
import subprocess
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.models import Script, ScriptTask
from ..models.schemas import ScriptTaskResponse
from ..core.config import settings


class ScriptService:
    def __init__(self):
        self.scripts_dir = settings.scripts_dir
        self.running_tasks: dict[int, asyncio.subprocess.Process] = {}

    async def register_script(
        self,
        db: AsyncSession,
        name: str,
        path: str,
        description: str = None,
        command_pattern: str = None
    ) -> Script:
        """注册一个新脚本"""
        script = Script(
            name=name,
            path=path,
            description=description,
            command_pattern=command_pattern or f"/{name}",
        )
        db.add(script)
        await db.commit()
        await db.refresh(script)
        return script

    async def get_all_scripts(self, db: AsyncSession) -> list[Script]:
        """获取所有可用脚本"""
        result = await db.execute(
            select(Script).where(Script.is_active == 1)
        )
        return list(result.scalars().all())

    async def get_script_by_pattern(
        self,
        db: AsyncSession,
        command_pattern: str
    ) -> Optional[Script]:
        """通过命令模式获取脚本"""
        result = await db.execute(
            select(Script).where(
                Script.command_pattern == command_pattern,
                Script.is_active == 1
            )
        )
        return result.scalar_one_or_none()

    async def execute_script(
        self,
        db: AsyncSession,
        script: Script,
        user_id: int
    ) -> ScriptTaskResponse:
        """执行脚本并返回任务信息"""
        from datetime import datetime

        # 创建任务记录
        task = ScriptTask(
            script_id=script.id,
            user_id=user_id,
            status="pending",
            started_at=datetime.utcnow()
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        # 异步执行脚本
        asyncio.create_task(self._run_script(task, script, db))

        return ScriptTaskResponse.model_validate(task)

    async def _run_script(
        self,
        task: ScriptTask,
        script: Script,
        db: AsyncSession
    ):
        """实际运行脚本的内部方法"""
        from datetime import datetime

        # 更新状态为运行中
        task.status = "running"
        await db.commit()

        script_path = Path(script.path)
        if not script_path.is_absolute():
            script_path = self.scripts_dir / script_path

        try:
            # 执行脚本
            process = await asyncio.create_subprocess_exec(
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.scripts_dir
            )

            # 设置超时
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=settings.max_script_runtime
                )

                task.exit_code = process.returncode
                task.output = stdout.decode('utf-8')
                task.error = stderr.decode('utf-8') if stderr else None

                if process.returncode == 0:
                    task.status = "completed"
                else:
                    task.status = "failed"

            except asyncio.TimeoutError:
                process.kill()
                task.status = "failed"
                task.error = f"Script execution timed out after {settings.max_script_runtime} seconds"

        except Exception as e:
            task.status = "failed"
            task.error = str(e)

        finally:
            task.completed_at = datetime.utcnow()
            await db.commit()

    async def get_task(
        self,
        db: AsyncSession,
        task_id: int
    ) -> Optional[ScriptTaskResponse]:
        """获取任务状态"""
        result = await db.execute(
            select(ScriptTask).where(ScriptTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        return ScriptTaskResponse.model_validate(task) if task else None


script_service = ScriptService()
