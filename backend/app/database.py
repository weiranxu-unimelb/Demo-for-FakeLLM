from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# 默认使用本地 SQLite，生产环境可通过环境变量 DATABASE_URL 切换到 PostgreSQL 等数据库
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine_kwargs = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

