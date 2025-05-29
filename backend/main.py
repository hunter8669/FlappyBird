from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import users, games, downloads

app = FastAPI(
    title="FlapPy Bird API",
    description="FlapPy Bird游戏后端API服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="../game-desktop"), name="static")

# API路由
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(games.router, prefix="/api/games", tags=["游戏数据"])
app.include_router(downloads.router, prefix="/api/downloads", tags=["下载服务"])

@app.get("/")
async def root():
    return {
        "message": "FlapPy Bird API服务运行中",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 