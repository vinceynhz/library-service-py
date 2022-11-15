"""
 :author: vic on 2021-10-23
"""
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Enum as SQLEnum

from .contributor import Contributor
from .book import Book
from .base import Base, BaseEnum


class ContributionType(BaseEnum):
    AUTHOR = "AUTHOR",
    ILLUSTRATOR = "ILLUSTRATOR",
    TRANSLATOR = "TRANSLATOR",
    PSEUDONYM = 'PSEUDONYM',
    EDITOR = 'EDITOR',
    COMPILER = 'COMPILER'


class BookContributor(Base):
    __tablename__ = 'book_contributor'
    book_id = Column(ForeignKey('book.id'), primary_key=True)
    contributor_id = Column(ForeignKey('contributor.id'), primary_key=True)
    contribution = Column(SQLEnum(ContributionType))
