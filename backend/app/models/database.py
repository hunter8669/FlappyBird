from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./flappybird.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class GameScore(Base):
    __tablename__ = "game_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    game_mode = Column(String)  # classic, timed, reverse, boss
    score = Column(Integer)
    play_time = Column(Float)  # 游戏时长(秒)
    created_at = Column(DateTime, default=datetime.utcnow)

class DownloadStats(Base):
    __tablename__ = "download_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String)  # windows, macos, linux, web
    version = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    download_time = Column(DateTime, default=datetime.utcnow)

# 创建所有表
def create_tables():
    Base.metadata.create_all(bind=engine)

# 获取数据库session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 