from Base import Base
from sqlalchemy.types import Integer, String, Enum
from sqlalchemy.schema import Column

class App(Base):
    STATUS_ACTIVE = 'active'
    STATUS_DELETED = 'deleted'

    __tablename__ = "app"
    appId = Column(Integer, primary_key=True)
    code = Column(String(50))
    name = Column(String(50))
    status = Column(Enum('admin', 'deleted'), default = 'active', nullable = False)