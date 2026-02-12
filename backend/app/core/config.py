from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8001

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./chat_auto.db"

    # 脚本目录
    scripts_dir: Path = Path(__file__).resolve().parent.parent.parent.parent / "scripts"

    # CORS（允许任意来源）
    cors_origins: list[str] = ["*"]

    # 安全配置
    max_script_runtime: int = 300  # 最大脚本执行时间(秒)
    allowed_exec_dir: str | None = None  # 限制脚本执行目录

    # JWT 密钥 (生产环境需使用环境变量)
    secret_key: str = "dev-secret-key-change-in-production"

    class Config:
        env_file = ".env"


settings = Settings()
