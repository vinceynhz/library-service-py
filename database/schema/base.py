"""
 :author: vic on 2021-04-17
"""
import enum

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseEnum(enum.Enum):
    @classmethod
    def parse(cls, string):
        for name, member in cls.__members__.items():
            if name.upper() == string.upper():
                return member
        raise NameError(f"No {cls.__name__} with value: " + string)
