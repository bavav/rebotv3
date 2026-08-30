# shared/app/models.py
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Float, Text, JSON
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class ErrorLog(Base):
    __tablename__ = "error_logs"
    id = Column(Integer, primary_key=True)
    bot_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String)
    source = Column(String)
    message = Column(Text)
    traceback = Column(Text, nullable=True)
    user_id = Column(BigInteger, nullable=True)
    chat_id = Column(BigInteger, nullable=True)
    meta = Column(JSON, nullable=True)

class MessageLog(Base):
    __tablename__ = "message_logs"
    id = Column(Integer, primary_key=True)
    bot_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    chat_id = Column(BigInteger)
    user_id = Column(BigInteger)
    text = Column(Text)
    is_ad = Column(Boolean, default=False)
    confidence = Column(Float, nullable=True)
    method = Column(String, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)