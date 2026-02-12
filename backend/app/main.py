from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.core.config import settings
from app.api.routes.scripts import router as scripts_router
from app.api.routes.messages import router as messages_router
from app.api.routes.websocket import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()

    # 注册一些示例脚本
    from app.core.database import async_session
    from app.services.script_service import script_service

    async with async_session() as db:
        # 检查是否已有脚本
        existing = await script_service.get_all_scripts(db)
        if not existing:
            await script_service.register_script(
                db=db,
                name="hello",
                path="hello.sh",
                description="输出 Hello World",
                command_pattern="/hello"
            )
            await script_service.register_script(
                db=db,
                name="system_info",
                path="system_info.sh",
                description="显示系统信息",
                command_pattern="/sysinfo"
            )
            await script_service.register_script(
                db=db,
                name="date",
                path="date.sh",
                description="显示当前时间和日期",
                command_pattern="/date"
            )

    yield
    # 关闭时的清理工作


app = FastAPI(
    title="ChatAuto API",
    description="通过聊天触发服务器脚本执行",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(scripts_router)
app.include_router(messages_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {
        "name": "ChatAuto",
        "version": "1.0.0",
        "description": "通过聊天触发服务器脚本执行的工具"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
