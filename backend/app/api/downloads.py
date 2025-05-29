from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.models.database import get_db, DownloadStats
import os
import platform

router = APIRouter()

@router.get("/desktop")
async def download_desktop(request: Request, db: Session = Depends(get_db)):
    """下载桌面版游戏"""
    
    # 检测用户系统
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host
    
    # 简单的系统检测逻辑
    if "Windows" in user_agent:
        platform_name = "windows"
        file_path = "../game-desktop/dist/flappybird-windows.zip"
    elif "Mac" in user_agent or "Darwin" in user_agent:
        platform_name = "macos"
        file_path = "../game-desktop/dist/flappybird-macos.zip"
    else:
        platform_name = "linux"
        file_path = "../game-desktop/dist/flappybird-linux.zip"
    
    # 记录下载统计
    download_stat = DownloadStats(
        platform=platform_name,
        version="1.2.0",
        ip_address=client_ip,
        user_agent=user_agent
    )
    db.add(download_stat)
    db.commit()
    
    # 返回文件（暂时返回game-desktop目录作为zip）
    if not os.path.exists("../game-desktop"):
        raise HTTPException(status_code=404, detail="游戏文件未找到")
    
    return {
        "message": "下载链接准备中",
        "platform": platform_name,
        "version": "1.2.0",
        "download_url": f"/api/downloads/file/{platform_name}"
    }

@router.get("/stats")
async def get_download_stats(db: Session = Depends(get_db)):
    """获取下载统计"""
    
    total_downloads = db.query(DownloadStats).count()
    
    platform_stats = {}
    platforms = ["windows", "macos", "linux", "web"]
    
    for platform_name in platforms:
        count = db.query(DownloadStats).filter(
            DownloadStats.platform == platform_name
        ).count()
        platform_stats[platform_name] = count
    
    return {
        "total_downloads": total_downloads,
        "platform_stats": platform_stats,
        "latest_version": "1.2.0"
    }

@router.get("/latest-version")
async def get_latest_version():
    """获取最新版本信息"""
    return {
        "version": "1.2.0",
        "release_date": "2023-10-15",
        "size": "~15MB",
        "features": [
            "Boss怒气系统",
            "Boss大招系统",
            "战斗平衡性调整",
            "Bug修复"
        ]
    } 