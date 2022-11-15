"""
 :author: vic on 2021-04-17
"""
import authority
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
        'first_name': str
    }
    __tablename__ = 'contributor'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)

    first_name = Column(String(128), nullable=False)
    last_names = Column(String(128))
    honorific = Column(String(10))

    cataloguing = Column(String(128), nullable=False)
    sha256 = Column(String(64), nullable=False, unique=True)

    @classmethod
    def maker(cls, data: dict) -> 'Contributor':
        first_name = authority.name(data['first_name'])

        if 'last_names' in data and len(data['last_names']) > 0:
            last_names = authority.name(data['last_names'])
        else:
            last_names = None

        if 'honorific' in data and len(data['honorific']) > 0:
            honorific = authority.name(data['honorific'])
        else:
            honorific = None

        cataloguing = authority.ordering_name(
            (last_names + ' ' if last_names is not None else '')
            + first_name
        )
        sha256 = authority.sha56(
            first_name
            + (' ' + last_names if last_names is not None else '')
            + (' ' + honorific if honorific is not None else '')
        )
        return Contributor(
            first_name=first_name,
            last_names=last_names,
            honorific=honorific,
            cataloguing=cataloguing,
            sha256=sha256
        )

    @classmethod
    def from_existing(cls, data: dict) -> 'Contributor':
        return Contributor(
            first_name=data['first_name'],
            last_names=data['last_names'],
            honorific=data['honorific'],
            cataloguing=data['cataloguing'],
            sha256=data['sha256']
        )

    def update(self, data: dict) -> bool:
        changed = False
        if 'first_name' in data and data['first_name'] is not None and len(data['first_name']) > 0:
            self.first_name = authority.name(data['first_name'])
            changed = True
        if 'last_names' in data:
            if data['last_names'] is None or len(data['last_names'].strip()) == 0:
                self.last_names = None
            else:
                self.last_names = authority.name(data['last_names'])
            changed = True
        if 'honorific' in data:
            if data['honorific'] is None or len(data['honorific'].strip()) == 0:
                self.honorific = None
            else:
                self.honorific = authority.name(data['honorific'])
            changed = True
        if changed:
            self.cataloguing = authority.ordering_name(
                (self.last_names + ' ' if self.last_names is not None else '')
                + self.first_name
            )
            self.sha256 = authority.sha56(
                self.first_name
                + (' ' + self.last_names if self.last_names is not None else '')
                + (' ' + self.honorific if self.honorific is not None else '')
            )
        return changed

    def json(self) -> dict:
        return {k: self._for_json(k) for k in self.__dir__() if k in (
            'id', 'sha256', 'first_name', 'last_names', 'honorific', 'cataloguing'
        )}

    def _for_json(self, attribute: str):
        value = getattr(self, attribute)
        return value

    def __repr__(self):
        return f"<Contributor(cataloguing='{self.cataloguing}')>"
