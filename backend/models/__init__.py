from sqlalchemy.orm import DeclarativeBase

class ModelBase(DeclarativeBase):
    pass

import models.movies

metadata = ModelBase.metadata