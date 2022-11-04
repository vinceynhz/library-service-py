"""
:author: vic on 2021-03-13
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .book_contributor import BookContributor, ContributionType
from .contributor import Contributor
from .book import Book, BookFormat
from .base import Base

import authority

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


def normalize_contributors(contributors: list):
    ids = set()
    result = []
    for entry in contributors:
        case_name = authority.name(entry)
        sha256 = authority.sha56(case_name)
        if sha256 not in ids:
            ids.add(sha256)
            cataloguing = authority.ordering_name(case_name)
            result.append({'name': case_name, 'cataloguing': cataloguing, 'sha256': sha256})
    return result


def normalize_books(books: list):
    result = {}
    for entry in books:
        raw_title = entry['title']
        raw_contributors = entry['contributors']

        clean_title = authority.title(raw_title)
        normalized_contributors = normalize_contributors(raw_contributors)

        unique_key = clean_title + "|" + "-".join([c['sha256'] for c in normalized_contributors])
        sha256 = authority.sha56(unique_key)

        if sha256 not in result:
            cataloguing = authority.ordering_title(raw_title)
            result[sha256] = ({
                'title': clean_title,
                'cataloguing': cataloguing,
                'sha256': sha256,
                'contributors': normalized_contributors,
                'isbn': entry['isbn'] if 'isbn' in entry else None,
                'year': entry['year'] if 'year' in entry else None,
                'language': entry['language'] if 'language' in entry else None
            })

    return result.values()


def search_contributors(names: list):
    with CloseableSession() as session:
        found = session.query(Contributor).filter(Contributor.name.in_(names)).all()
        result = [c.json() for c in found]
        return result
