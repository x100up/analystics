from Base import Base
from sqlalchemy import Column, Integer, String, Enum


class App(Base):
    __tablename__ = "app"
    appId = Column(Integer, primary_key=True)
    code = Column(String(50))
    name = Column(String(50))