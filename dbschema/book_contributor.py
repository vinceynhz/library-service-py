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
    TRANSLATOR = "TRANSLATOR"


class BookContributor(Base):
    __tablename__ = 'book_flan_contributor'
    book_id = Column(ForeignKey('book.id'), primary_key=True)
    contributor_id = Column(ForeignKey('contributor.id'), primary_key=True)
    contribution = Column(SQLEnum(ContributionType))
    book = relationship(Book, back_populates="contributors")
    contributor = relationship(Contributor, back_populates="books")

    def contributor_json(self):
        return {
            'id': self.contributor_id,
            'sha256': self.contributor.sha256,
            'type': self.contribution.name
        }

    def book_json(self):
        return {
            'id': self.book_id,
            'sha256': self.book.sha256,
            'type': self.contribution.name
        }
