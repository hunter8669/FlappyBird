from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    """获取用户列表"""
    return {"message": "用户管理功能开发中"}

@router.post("/register")
async def register_user():
    """用户注册"""
    return {"message": "用户注册功能开发中"}

@router.post("/login")
async def login_user():
    """用户登录"""
    return {"message": "用户登录功能开发中"} 