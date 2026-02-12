# ChatAuto - 聊天触发脚本执行工具

类似 Rocket.Chat，通过聊天命令触发服务器脚本执行。

## 技术栈
- 前端: Vue 3 + TypeScript
- 后端: Python FastAPI
- 数据库: SQLite
- 通信: WebSocket

## 项目结构
```
chat-auto/
├── backend/          # 后端服务
│   └── app/
│       ├── api/      # API 路由
│       ├── models/   # 数据模型
│       ├── core/     # 配置
│       ├── services/ # 业务逻辑
│       └── main.py   # 入口
├── frontend/         # 前端应用
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── api/
│       └── stores/
└── scripts/          # 可执行脚本目录
```

## 快速启动

### 后端
```bash
cd backend

python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python app/main.py
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 使用斜杠命令
- `/list` - 查看可用脚本
- `/run <script_name>` - 执行脚本
- `/status <task_id>` - 查看任务状态
