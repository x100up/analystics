__author__ = 'prog-31'
from models.Worker import Worker
from models.User import User
from sqlalchemy import create_engine

engine = create_engine('mysql://root:123123@127.0.0.1/analystic')
User.metadata.create_all(engine)
Worker.metadata.create_all(engine)
