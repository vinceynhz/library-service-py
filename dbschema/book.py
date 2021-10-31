"""
 :author: vic on 2021-04-17
"""
import authority
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Sequence, Enum as SQLEnum
from .base import Base, BaseEnum


class BookFormat(BaseEnum):
    PAPERBACK = "PAPERBACK"
    HARDBACK = "HARDBACK"
    AUDIOBOOK = "AUDIOBOOK"
    EBOOK = "EBOOK"


class Book(Base):
    required = {
        'format': str,
        'title': str,
        'contributors': dict
    }

    __tablename__ = 'book'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    sha256 = Column(String(64), nullable=False, unique=True)
    cataloguing = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    isbn = Column(String(20))
    year = Column(String(4))
    language = Column(String(5))
    format = Column(SQLEnum(BookFormat), nullable=False)
    contributors = relationship(
        "BookContributor",
        back_populates="book"
    )

    @classmethod
    def maker(cls, data: dict):
        book_format = BookFormat.parse(data['format'])
        raw_title = data['title']
        clean_title = authority.title(raw_title)
        ordering_title = authority.ordering_title(raw_title)
        return Book(title=clean_title,
                    cataloguing=ordering_title,
                    format=book_format,
                    # sha256
                    isbn=data['isbn'] if 'isbn' in data else None,
                    year=data['year'] if 'year' in data else None,
                    language=data['language'] if 'language' in data else None
                    )

    def generate_sha256(self):
        unique_key = self.title + "|" \
                     + self.format.name + "|" \
                     + "-".join([c.contributor.sha256 for c in self.contributors])
        self.sha256 = authority.sha56(unique_key)

    def json(self):
        return {k: self._for_json(k) for k in self.__dir__() if k in (
            'id', 'sha256', 'cataloguing', 'title', 'isbn', 'year', 'language', 'format', 'contributors'
        )}

    def _for_json(self, attribute: str):
        value = getattr(self, attribute)
        if attribute == 'format':
            return value.name
        if attribute == 'contributors':
            return [c.contributor_json() for c in value]
        return value

    def __repr__(self):
        return f"<Book(cataloguing='{self.cataloguing}', title='{self.title}', format='{self.format.name}'>"
