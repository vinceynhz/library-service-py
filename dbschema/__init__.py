"""
:author: vic on 2021-03-13
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .book_contributor import BookContributor, ContributionType
from .contributor import Contributor
from .book import Book

from .base import Base

Engine = create_engine('sqlite:///database/library.db', echo=True)
SessionMaker = sessionmaker(bind=Engine)


class CloseableSession(object):
    def __init__(self):
        self.session = SessionMaker()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


def get_contributors():
    with CloseableSession() as session:
        result = session.query(Contributor).all()
        return [c.json() for c in result]


def get_contributor(contributor_id: int):
    with CloseableSession() as session:
        result = session.query(Contributor).filter(Contributor.id == contributor_id).first()
        return result.json() if result is not None else None


def add_contributor(new_contributor: Contributor):
    with CloseableSession() as session:
        # ez pz slice of ch-z
        session.add(new_contributor)
        session.commit()
        return str(new_contributor.id)


def get_books():
    with CloseableSession() as session:
        result = session.query(Book).all()
        return [b.json() for b in result]


def get_book(book_id: int):
    with CloseableSession() as session:
        result = session.query(Book).filter(Book.id == book_id).first()
        return result.json() if result is not None else None


def add_book(new_book: Book, contributors: dict):
    with CloseableSession() as session:
        # get the managed contributors to be added
        ids_to_search = contributors.keys()
        found_contributors = session.query(Contributor).filter(Contributor.id.in_(ids_to_search)).all()
        assert found_contributors is not None and len(found_contributors) > 0

        # create associations
        for found in found_contributors:
            # get the type of contribution
            contribution_type = ContributionType.parse(contributors[str(found.id)])
            # create the contribution
            contribution = BookContributor(contribution=contribution_type, contributor=found)
            new_book.contributors.append(contribution)

        new_book.generate_sha256()

        # add the book to the database
        session.add(new_book)
        session.commit()

        return str(new_book.id)
