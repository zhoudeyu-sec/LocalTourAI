import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 优先读取环境变量，没有则使用默认值
SQLALCHEMY_DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL",
    "mysql+pymysql://root:123456@127.0.0.1:3306/scenic_digital_human",
)
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()