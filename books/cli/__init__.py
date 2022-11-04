"""
 :author: vic on 2022-09-25
"""

import os
import sys
import json
import logging

import authority
import books.openlibrary as openlibrary

from dbschema.book import BookFormat

__win__ = 'win' in sys.platform
os.system("")


class Color(object):
    RESET = u"\u001b[0m"
    BLACK = u"\u001b[30;1m"
    RED = u"\u001b[31;1m"
    GREEN = u"\u001b[32;1m"
    YELLOW = u"\u001b[33;1m"
    BLUE = u"\u001b[34;1m"
    MAGENTA = u"\u001b[35;1m"
    CYAN = u"\u001b[36;1m"
    WHITE = u"\u001b[37;1m"


class Action(object):
    BOOK = f"{Color.MAGENTA}[book]{Color.RESET} "
    FIND = f"{Color.MAGENTA}[find]{Color.RESET} "
    EDIT = f"{Color.MAGENTA}[edit]{Color.RESET} "
    ADD = f"{Color.MAGENTA}[ add]{Color.RESET} "
    VIEW = f"{Color.MAGENTA}[view]{Color.RESET} "
    SAVE = f"{Color.MAGENTA}[save]{Color.RESET} "
    CONFIRM = f"{Color.MAGENTA}[vald]{Color.RESET} "
    CONFIG = f"{Color.MAGENTA}[conf]{Color.RESET} "


def create_book(config: dict):
    title = input(f"{Color.BLUE}       Title: {Color.RESET}").strip()
    author = input(f"{Color.BLUE}       Author: {Color.RESET}").strip().split(",")
    isbn = input(f"{Color.BLUE}       ISBN: {Color.RESET}").strip()
    year = input(f"{Color.BLUE}       Year: {Color.RESET}").strip()
    language = input(
        f"{Color.BLUE}       Language ({authority.desc_lang(config['language'])}): {Color.RESET}").strip()
    if len(language) == 0:
        language = config['language']
    bf = input(
        f"{Color.BLUE}       Format({config['book_format']}) "
        f"[P]aperback/[H]ardback/[A]udiobook/[E]book: {Color.RESET}"
    ).strip()
    book_format = BookFormat.parse(config['book_format'])
    if len(bf) != 0:
        for name, member in BookFormat.__members__.items():
            if name.lower()[0] == bf.lower()[0]:
                book_format = member

    return openlibrary.Book(
        title,
        author,
        isbn,
        language,
        year,
        book_format
    )


def update_config(config: dict):
    print(f"{Action.CONFIG}Enter defaults (enter to keep existing value)")
    language = input(
        f"{Color.BLUE}       Language ({authority.desc_lang(config['language'])}): {Color.RESET}"
    ).strip()
    if len(language) != 0:
        config['language'] = authority.match_lang(language)

    book_format = input(
        f"{Color.BLUE}       Format({config['book_format']}) "
        f"[P]aperback/[H]ardback/[A]udiobook/[E]book: {Color.RESET}"
    ).strip()
    if len(book_format) != 0:
        for name, member in BookFormat.__members__.items():
            if name.lower()[0] == book_format.lower()[0]:
                config['book_format'] = name

    db_file = input(
        f"{Color.BLUE}       DB File({config['db_file']}): {Color.RESET}"
    ).strip()
    if len(db_file) != 0:
        config['db_file'] = db_file

    with open('./database/config.json', 'w+') as outfile:
        json.dump(config, outfile, indent=4, sort_keys=True)
    print(f"{Action.CONFIG}Config updated")


def save_book(book: openlibrary.Book, config: dict):
    with open(config['db_file'], "a+") as outfile:
        outfile.write(json.dumps(book.json(), sort_keys=True, ensure_ascii=False))
        outfile.write("\n")

    print(f"{Action.SAVE}Book saved!")


def edit_book(book: openlibrary.Book, config: dict):
    print(f"{Action.EDIT}Enter book details (enter to keep existing value)")
    print(f"{Action.EDIT}{book.get_title()}")
    title = input(f"{Color.BLUE}       Title: {Color.RESET}").strip()
    if len(title) != 0:
        book.set_title(title)

    print(f"{Action.EDIT}{','.join(book.get_author())}")
    author = input(f"{Color.BLUE}       Author: {Color.RESET}").strip()
    if len(author) != 0:
        book.set_author(author)

    print(f"{Action.EDIT}{book.get_isbn()}")
    isbn = input(f"{Color.BLUE}       ISBN: {Color.RESET}").strip()
    if len(isbn) != 0:
        book.set_isbn(isbn)

    print(f"{Action.EDIT}{book.get_year()}")
    year = input(f"{Color.BLUE}       Year: {Color.RESET}").strip()
    if len(year) != 0:
        book.set_year(year)

    print(f"{Action.EDIT}{book.get_language()}")
    language = input(f"{Color.BLUE}       Language: {Color.RESET}").strip()
    if len(language) != 0:
        book.set_language(language)

    print(f"{Action.EDIT}{book.get_book_format().name}")
    book_format = input(
        f"{Color.BLUE}       Format [P]aperback/[H]ardback/[A]udiobook/[E]book: {Color.RESET}"
    ).strip()
    if len(book_format) != 0:
        book.set_book_format(book_format)

    book.generate_sha256()
    print(f"{Action.EDIT}{book}")
    save_book(book, config)


def confirm_book(book: openlibrary.Book, config: dict):
    print(f"{Action.CONFIRM}{book}")
    action = input(f"{Action.CONFIRM}{Color.BLUE}[S]ave/[E]dit/[D]iscard]: {Color.RESET}").strip()
    if len(action) > 0:
        action = action.lower()[0]
        if action == 's':
            save_book(book, config)
        elif action == 'e':
            edit_book(book, config)


def search_book(param: str, config: dict):
    print(f"{Action.FIND}Searching...")
    try:
        new_book = openlibrary.search(param, config)
        confirm_book(new_book, config)
    except openlibrary.SearchException as error:
        print(f"{Action.FIND}{Color.YELLOW}{error}{Color.RESET}")
        return


def add_book(config):
    print(f"{Action.ADD}Enter new book details")
    new_book = create_book(config)
    confirm_book(new_book, config)


def view_book():
    print(f"{Action.VIEW}")


def run():
    logging.basicConfig(level=logging.DEBUG, filename='./cli.log')
    if not __win__:
        import readline
        import atexit
        hist_file = os.path.join(os.path.expanduser("~"), ".python_history")
        try:
            readline.read_history_file(hist_file)
        except FileNotFoundError:
            pass
        atexit.register(readline.write_history_file, hist_file)

    print()
    print(f"{Action.CONFIG}Reading default config")
    try:
        with open('./database/config.json', 'r') as infile:
            config = json.load(infile)
        print(f"{Action.CONFIG}Config loaded")
    except FileNotFoundError:
        print(f"{Action.CONFIG}Default config not set, creating one")
        config = {
            'db_file': './database/books.cli.db',
            'language': 'eng',
            'book_format': 'HARDBACK'
        }
        with open('./database/config.json', 'w+') as outfile:
            json.dump(config, outfile, indent=2)

    while True:
        try:
            entry = input(f"{Action.BOOK}").strip().lower()
            if len(entry) == 0:
                continue
            if entry in ["exit", "quit", "bye", "done"]:
                break
            if entry == "add":
                add_book(config)
            elif entry == "view":
                view_book()
            elif entry.startswith("conf"):
                update_config(config)
            else:
                search_book(entry, config)
        except KeyboardInterrupt:
            print()
            pass
        except KeyError as error:
            print(f"{Color.YELLOW}{error}{Color.RESET}")
        except AttributeError as error:
            print(f"{Color.YELLOW}{error}{Color.RESET}")
        except (Exception,) as error:
            print(f"{Color.RED}ERROR:{Color.RESET} {error}")
            logging.exception("Error")

    print()
