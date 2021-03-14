"""
:author: vic on 2021-03-13
"""
import authority

from sqlalchemy import Column, Integer, String, Sequence, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Engine = create_engine('sqlite:///database/library.db', echo=True)
SessionMaker = sessionmaker(bind=Engine)
Base = declarative_base()


class CloseableSession(object):
    def __init__(self):
        self.session = SessionMaker()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


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
    __tablename__ = 'contributor'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    sha256 = Column(String(64))
    name = Column(String(255))
    cataloguing = Column(String(255))

    @classmethod
    def maker(cls, data):
        case_name = authority.name(data['name'])
        cataloguing = authority.ordering_name(data['name'])
        sha256 = authority.sha56(case_name)

        return Contributor(name=case_name, cataloguing=cataloguing, sha256=sha256)

    def json(self):
        return {k: getattr(self, k) for k in self.__dir__() if k in ('id', 'sha256', 'name', 'cataloguing')}

    def __repr__(self):
        return "<Contributor(cataloguing='%s', name='%s')>" % (self.cataloguing, self.name)


def contributors():
    with CloseableSession() as session:
        result = session.query(Contributor).all()
    return [c.json() for c in result]


def add_contributor(contributor):
    with CloseableSession() as session:
        session.add(contributor)
        session.commit()
    return contributor
