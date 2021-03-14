"""
 :author: vic on 2021-03-13
"""
import re
import hashlib

_articles = {"a", "an", "of", "the", "is", "in", "to"}
_title_articles = {"a", "an", "the"}
_honorifics = {"sir", "sire", "mrs", "miss", "ms", "lord", "dr", "phd", "dphil", "md", "do", "doc", "sr", "jr"}
_roman = re.compile("^m{0,3}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$")


def _isalphanum(char):
    return char.isalpha() or char.isdigit() or char == ' '


def _capitalize(word, force=False, articles=False):
    """
    These are the capitalization rules:
    - The first alphabetic character ([a-z]) will be set to upper case, the rest to lower case, except for the following
    cases
    - If the word already contains 2 or more upper case characters (as in the case of acronyms) no change will be made,
    unless force flag is set
    - If the word is a valid roman numeral as defined by authority._romans, the word will be returned in all upper case
    - If the word is a valid article it will depend on the flag passed whether the first capitalization rule is applied.
    :param word: to capitalize
    :param force: whether more than one capital letter should be ignored (as in acronyms)
    :param articles: whether articles should be capitalized
    :return: a capitalized word as described before.
    """
    if not force and len([c.isalpha() and c.isupper for c in word]) >= 2:
        # If the word already has 2 upper case letters, we wont do anything for it and we'll leave it unchanged
        return word
    lower_word = word.lower()
    if _roman.match(lower_word) is not None:
        return word.upper()
    if not articles and lower_word in _articles:
        return lower_word
    return word.title()


def _normalize(string):
    return ''.join([c.lower() for c in string if _isalphanum(c)])


def name(string):
    """
    :param string: to convert to proper case
    :return: author name capitalized
    """
    words = [_capitalize(w, force=True) for w in string.split(' ')]
    return ' '.join(words)


def ordering_name(string):
    """
    :param string: name of an author to normalize and order
    :return: containing the author name in normalized form removing any honorifics or roman numerals from the name and
    starting from the first last name
    """
    words = [w for w in _normalize(string).split(' ') if w not in _honorifics and _roman.match(w) is None]
    words.append(words.pop(0))
    return ' '.join(words)


def sha56(string):
    return hashlib.sha256(_normalize(string).encode('utf-8')).hexdigest().upper()
