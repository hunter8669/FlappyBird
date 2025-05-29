from fastapi import APIRouter

router = APIRouter()

@router.get("/scores")
async def get_scores():
    """获取游戏分数"""
    return {"message": "分数查询功能开发中"}

@router.post("/scores")
async def save_score():
    """保存游戏分数"""
    return {"message": "分数保存功能开发中"}

@router.get("/leaderboard")
async def get_leaderboard():
    """获取排行榜"""
    return {"message": "排行榜功能开发中"} 