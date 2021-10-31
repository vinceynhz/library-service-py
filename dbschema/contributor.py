"""
 :author: vic on 2021-04-17
"""
import authority
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Sequence
from .base import Base


class Contributor(Base):
    """
    Notes on contributor entities:

    Normalization
    Contributor names are going to be normalized according to the rules of title casing defined in authority.titleCase.

    Ordering
    The string used for alphabetical cataloguing will be determined according to the rules defined in
    authority.contributorForOrdering

    Please note that two or more contributors may yield the same cataloguing value:
    - Diane Maxwell
    - Dr. Diane Maxwell
    - Diane Maxwell Jr.
    - Diane Maxwell III

    All above names would be ordered as "maxwell diane" once all honorifics, special characters and roman numerals are
    removed.

    Uniqueness
    A contributor uniqueness is determined by the authority.sha256 function over the normalized version of the
    contributor's name as described above.

    The case for homonym contributors is still to be determined
    """
    required = {
        'name': str
    }
    __tablename__ = 'contributor'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    sha256 = Column(String(64), nullable=False, unique=True)
    cataloguing = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    books = relationship(
        "BookContributor",
        back_populates="contributor"
    )

    @classmethod
    def maker(cls, data: dict):
        case_name = authority.name(data['name'])
        cataloguing = authority.ordering_name(data['name'])
        sha256 = authority.sha56(case_name)
        return Contributor(name=case_name, cataloguing=cataloguing, sha256=sha256, books=[])

    def json(self):
        return {k: self._for_json(k) for k in self.__dir__() if k in (
            'id', 'sha256', 'name', 'cataloguing', 'books'
        )}

    def _for_json(self, attribute: str):
        value = getattr(self, attribute)
        if attribute == 'books':
            return [b.book_json() for b in value]
        return value

    def __repr__(self):
        return f"<Contributor(cataloguing='{self.cataloguing}', name='{self.name}')>"
