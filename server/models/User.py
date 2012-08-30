from Base import Base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Enum


class User(Base):
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'

    __tablename__ = "user"
    userId = Column(Integer, primary_key=True)
    login = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(50))
    role = Column(Enum('admin', 'user'), default='user')


