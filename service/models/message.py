from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = "message"

    id = Column(String, primary_key=True, index=True)
    payload = Column(String)
    created_at = Column(TIMESTAMP)
    processed_by = Column(String)
