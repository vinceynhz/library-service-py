import requests
import authority

from dbschema.book import BookFormat
from typing import Union


class SearchException(Exception):
    """ To capture errors during ineractions with the open library """


class Book(object):
    def __init__(self, title: str, author: list, isbn: str = None, language: str = None, year: str = None,
                 book_format: BookFormat = BookFormat.PAPERBACK):
        self._title = authority.title(title)
        self._catalogue_title = authority.ordering_title(title)

        self._author = [authority.name(a) for a in author]
        self._catalogue_author = [authority.ordering_name(a) for a in author]

        self._isbn = isbn
        self._language = authority.match_lang(language)
        self._year = year
        self._book_format = book_format
        self._sha256 = ""
        self.generate_sha256()

    def generate_sha256(self):
        unique_key = self._title + "|" \
                     + self._book_format.name + "|" \
                     + "-".join([authority.sha56(a) for a in self._author])
        self._sha256 = authority.sha56(unique_key)

    def json(self):
        return {k[1:]: self._for_json(k) for k in self.__dir__() if k in (
            '_sha256', '_title', '_catalogue_title', '_author', '_catalogue_author', '_isbn', '_language', '_year',
            '_book_format'
        )}

    @classmethod
    def from_json(cls, json_book: dict):
        return Book(
            json_book['title'],
            json_book['author'],
            json_book['isbn'],
            json_book['language'],
            json_book['year'],
            BookFormat.parse(BookFormat.parse(json_book['book_format']))
        )

    def get_title(self):
        return self._title

    def set_title(self, title: str):
        self._title = authority.title(title)
        self._catalogue_title = authority.ordering_title(title)

    def get_author(self):
        return self._author

    def set_author(self, author: Union[str, list]):
        if type(author) is str:
            author = author.split(",")
        self._author = [authority.name(a) for a in author]
        self._catalogue_author = [authority.ordering_name(a) for a in author]

    def get_isbn(self):
        return self._isbn

    def set_isbn(self, isbn: str):
        self._isbn = isbn

    def get_year(self):
        return self._year

    def set_year(self, year: str):
        self._year = year

    def get_language(self):
        return self._language

    def set_language(self, language: str):
        self._language = authority.match_lang(language)

    def get_book_format(self):
        return self._book_format

    def set_book_format(self, book_format: Union[str, BookFormat]):
        if type(book_format) is str:
            self._book_format = book_format_initial(book_format)
        if type(book_format) is BookFormat:
            self._book_format = book_format

    def _for_json(self, attribute: str):
        value = getattr(self, attribute)
        if attribute == '_book_format':
            return value.name
        return value

    def __repr__(self):
        return f'"{self._title}", {", ".join(self._author)}\n       ISBN:{self._isbn}, {self._year}, ' \
               f'{authority.desc_lang(self._language)}, {self._book_format.name}'


def search(param: str, config: dict):
    isbn = None
    if authority.is_num(param):
        isbn = param
        param = "isbn:" + param
    elif param.lower().startswith("isbn:"):
        isbn = param.split(":")[1]
    elif ':' not in param:
        raise SearchException("Ambiguous search, use field names to narrow query")

    params = {
        'q': param,
        'fields': 'title,author_name,language,publish_year,isbn',
        'limit': 1
    }
    result = requests.get("http://openlibrary.org/search.json", params=params)

    if result.status_code != requests.codes.ok:
        result.raise_for_status()

    try:
        data = result.json()
    except requests.exceptions.JSONDecodeError as error:
        if hasattr(error, 'message'):
            raise SearchException(error.message)
        else:
            raise SearchException(str(error))

    if 'numFound' not in data or data['numFound'] == 0:
        raise SearchException("No results found")

    data = data['docs'][0]

    title = data['title']
    author = data['author_name'] if 'author_name' in data else []

    if isbn is None:
        isbn = data['isbn'] if 'isbn' in data else []
        if len(isbn) > 0:
            isbn.sort()
            isbn = isbn[-1]
        else:
            isbn = ""

    if 'language' in data:
        if 'eng' in data['language']:
            language = 'eng'
        elif "spa" in data['language']:
            language = 'spa'
        else:
            language = data['language'][0]
    else:
        language = config['language']

    year = data['publish_year'][-1] if 'publish_year' in data else ""

    return Book(
        title,
        author,
        isbn,
        language,
        year,
        BookFormat.parse(config['book_format'])
    )


def book_format_initial(param: str) -> BookFormat:
    for name, member in BookFormat.__members__.items():
        if name.lower()[0] == param.lower()[0]:
            return member
    raise NameError(f"No BookFormat with initial: {param.upper()}")
