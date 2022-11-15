"""
 :author: vic on 2021-03-13
"""
import re
import hashlib

_articles = {"a", "an", "of", "the", "is", "in", "to"}
_title_articles = {"a", "an", "the"}
_honorifics = {"sir", "sire", "mrs", "miss", "ms", "lord", "dr", "phd", "dphil", "md", "do", "doc", "sr", "jr"}
_roman = re.compile("^m{0,3}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$")

_iso_639_2 = {
    "aar": "Afar",
    "abk": "Abkhazian",
    "ace": "Achinese",
    "ach": "Acoli",
    "ada": "Adangme",
    "ady": "Adyghe",
    "afa": "Afro-Asiatic",
    "afh": "Afrihili",
    "afr": "Afrikaans",
    "ain": "Ainu",
    "aka": "Akan",
    "akk": "Akkadian",
    "ale": "Aleut",
    "alg": "Algonquian",
    "alt": "Southern Altai",
    "amh": "Amharic",
    "ang": "English",
    "anp": "Angika",
    "apa": "Apache",
    "ara": "Arabic",
    "arc": "Official Aramaic (700–300 BCE)",
    "arg": "Aragonese",
    "arn": "Mapudungun",
    "arp": "Arapaho",
    "art": "Artificial",
    "arw": "Arawak",
    "asm": "Assamese",
    "ast": "Asturian",
    "ath": "Athapascan",
    "aus": "Australian",
    "ava": "Avaric",
    "ave": "Avestan",
    "awa": "Awadhi",
    "aym": "Aymara",
    "aze": "Azerbaijani",
    "bad": "Banda",
    "bai": "Bamileke",
    "bak": "Bashkir",
    "bal": "Baluchi",
    "bam": "Bambara",
    "ban": "Balinese",
    "bas": "Basa",
    "bat": "Baltic",
    "bej": "Beja",
    "bel": "Belarusian",
    "bem": "Bemba",
    "ben": "Bengali",
    "ber": "Berber",
    "bho": "Bhojpuri",
    "bih": "Bihari",
    "bik": "Bikol",
    "bin": "Bini",
    "bis": "Bislama",
    "bla": "Siksika",
    "bnt": "Bantu",
    "bod_tib": "Tibetan",
    "bos": "Bosnian",
    "bra": "Braj",
    "bre": "Breton",
    "btk": "Batak",
    "bua": "Buriat",
    "bug": "Buginese",
    "bul": "Bulgarian",
    "byn": "Blin",
    "cad": "Caddo",
    "cai": "Central American Indian",
    "car": "Galibi Carib",
    "cat": "Catalan",
    "cau": "Caucasian",
    "ceb": "Cebuano",
    "cel": "Celtic",
    "ces_cze": "Czech",
    "cha": "Chamorro",
    "chb": "Chibcha",
    "che": "Chechen",
    "chg": "Chagatai",
    "chk": "Chuukese",
    "chm": "Mari",
    "chn": "Chinook jargon",
    "cho": "Choctaw",
    "chp": "Chipewyan",
    "chr": "Cherokee",
    "chu": "Church Slavic",
    "chv": "Chuvash",
    "chy": "Cheyenne",
    "cmc": "Chamic",
    "cnr": "Montenegrin",
    "cop": "Coptic",
    "cor": "Cornish",
    "cos": "Corsican",
    "cpe": "Creoles and pidgins",
    "cpf": "Creoles and pidgins",
    "cpp": "Creoles and pidgins",
    "cre": "Cree",
    "crh": "Crimean Tatar",
    "crp": "Creoles and pidgins",
    "csb": "Kashubian",
    "cus": "Cushitic",
    "cym_wel": "Welsh",
    "dak": "Dakota",
    "dan": "Danish",
    "dar": "Dargwa",
    "day": "Land Dayak",
    "del": "Delaware",
    "den": "Slave (Athapascan)",
    "deu_ger": "German",
    "dgr": "Dogrib",
    "din": "Dinka",
    "div": "Divehi",
    "doi": "Dogri",
    "dra": "Dravidian",
    "dsb": "Lower Sorbian",
    "dua": "Duala",
    "dum": "Dutch",
    "dyu": "Dyula",
    "dzo": "Dzongkha",
    "efi": "Efik",
    "egy": "Egyptian (Ancient)",
    "eka": "Ekajuk",
    "ell_gre": "Greek",
    "elx": "Elamite",
    "eng": "English",
    "enm": "English",
    "epo": "Esperanto",
    "est": "Estonian",
    "eus_baq": "Basque",
    "ewe": "Ewe",
    "ewo": "Ewondo",
    "fan": "Fang",
    "fao": "Faroese",
    "fas_per": "Persian",
    "fat": "Fanti",
    "fij": "Fijian",
    "fil": "Filipino",
    "fin": "Finnish",
    "fiu": "Finno-Ugrian",
    "fon": "Fon",
    "fra_fre": "French",
    "frm": "French",
    "fro": "French",
    "frr": "Northern Frisian",
    "frs": "East Frisian Low Saxon",
    "fry": "Western Frisian",
    "ful": "Fulah",
    "fur": "Friulian",
    "gaa": "Ga",
    "gay": "Gayo",
    "gba": "Gbaya",
    "gem": "Germanic",
    "gez": "Geez",
    "gil": "Gilbertese",
    "gla": "Gaelic",
    "gle": "Irish",
    "glg": "Galician",
    "glv": "Manx",
    "gmh": "German",
    "goh": "German",
    "gon": "Gondi",
    "gor": "Gorontalo",
    "got": "Gothic",
    "grb": "Grebo",
    "grc": "Greek",
    "grn": "Guarani",
    "gsw": "Swiss German",
    "guj": "Gujarati",
    "gwi": "Gwich'in",
    "hai": "Haida",
    "hat": "Haitian",
    "hau": "Hausa",
    "haw": "Hawaiian",
    "heb": "Hebrew",
    "her": "Herero",
    "hil": "Hiligaynon",
    "him": "Himachali",
    "hin": "Hindi",
    "hit": "Hittite",
    "hmn": "Hmong",
    "hmo": "Hiri Motu",
    "hrv": "Croatian",
    "hsb": "Upper Sorbian",
    "hun": "Hungarian",
    "hup": "Hupa",
    "hye_arm": "Armenian",
    "iba": "Iban",
    "ibo": "Igbo",
    "ido": "Ido",
    "iii": "Sichuan Yi",
    "ijo": "Ijo",
    "iku": "Inuktitut",
    "ile": "Interlingue",
    "ilo": "Iloko",
    "ina": "Interlingua (International Auxiliary Language Association)",
    "inc": "Indo-Aryan",
    "ind": "Indonesian",
    "ine": "Indo-European",
    "inh": "Ingush",
    "ipk": "Inupiaq",
    "ira": "Iranian",
    "iro": "Iroquoian",
    "isl_ice": "Icelandic",
    "ita": "Italian",
    "jav": "Javanese",
    "jbo": "Lojban",
    "jpn": "Japanese",
    "jpr": "Judeo-Persian",
    "jrb": "Judeo-Arabic",
    "kaa": "Kara-Kalpak",
    "kab": "Kabyle",
    "kac": "Kachin",
    "kal": "Kalaallisut",
    "kam": "Kamba",
    "kan": "Kannada",
    "kar": "Karen",
    "kas": "Kashmiri",
    "kat_geo": "Georgian",
    "kau": "Kanuri",
    "kaw": "Kawi",
    "kaz": "Kazakh",
    "kbd": "Kabardian",
    "kha": "Khasi",
    "khi": "Khoisan",
    "khm": "Central Khmer",
    "kho": "Khotanese",
    "kik": "Kikuyu",
    "kin": "Kinyarwanda",
    "kir": "Kirghiz",
    "kmb": "Kimbundu",
    "kok": "Konkani",
    "kom": "Komi",
    "kon": "Kongo",
    "kor": "Korean",
    "kos": "Kosraean",
    "kpe": "Kpelle",
    "krc": "Karachay-Balkar",
    "krl": "Karelian",
    "kro": "Kru",
    "kru": "Kurukh",
    "kua": "Kuanyama",
    "kum": "Kumyk",
    "kur": "Kurdish",
    "kut": "Kutenai",
    "lad": "Ladino",
    "lah": "Lahnda",
    "lam": "Lamba",
    "lao": "Lao",
    "lat": "Latin",
    "lav": "Latvian",
    "lez": "Lezghian",
    "lim": "Limburgan",
    "lin": "Lingala",
    "lit": "Lithuanian",
    "lol": "Mongo",
    "loz": "Lozi",
    "ltz": "Luxembourgish",
    "lua": "Luba-Lulua",
    "lub": "Luba-Katanga",
    "lug": "Ganda",
    "lui": "Luiseno",
    "lun": "Lunda",
    "luo": "Luo (Kenya and Tanzania)",
    "lus": "Lushai",
    "mad": "Madurese",
    "mag": "Magahi",
    "mah": "Marshallese",
    "mai": "Maithili",
    "mak": "Makasar",
    "mal": "Malayalam",
    "man": "Mandingo",
    "map": "Austronesian",
    "mar": "Marathi",
    "mas": "Masai",
    "mdf": "Moksha",
    "mdr": "Mandar",
    "men": "Mende",
    "mga": "Irish",
    "mic": "Mi'kmaq",
    "min": "Minangkabau",
    "mis": "Uncoded",
    "mkd_mac": "Macedonian",
    "mkh": "Mon-Khmer",
    "mlg": "Malagasy",
    "mlt": "Maltese",
    "mnc": "Manchu",
    "mni": "Manipuri",
    "mno": "Manobo",
    "moh": "Mohawk",
    "mon": "Mongolian",
    "mos": "Mossi",
    "mri_mao": "Māori",
    "msa_may": "Malay",
    "mul": "Multiple",
    "mun": "Munda",
    "mus": "Creek",
    "mwl": "Mirandese",
    "mwr": "Marwari",
    "mya_bur": "Burmese",
    "myn": "Mayan",
    "myv": "Erzya",
    "nah": "Nahuatl",
    "nai": "North American Indian",
    "nap": "Neapolitan",
    "nau": "Nauru",
    "nav": "Navajo",
    "nbl": "Ndebele",
    "nde": "Ndebele",
    "ndo": "Ndonga",
    "nds": "Low German",
    "nep": "Nepali",
    "new": "Nepal Bhasa",
    "nia": "Nias",
    "nic": "Niger-Kordofanian",
    "niu": "Niuean",
    "nld_dut": "Dutch",
    "nno": "Norwegian Nynorsk",
    "nob": "Bokmål",
    "nog": "Nogai",
    "non": "Norse",
    "nor": "Norwegian",
    "nqo": "N\'Ko",
    "nso": "Pedi",
    "nub": "Nubian",
    "nwc": "Classical Newari",
    "nya": "Chichewa",
    "nym": "Nyamwezi",
    "nyn": "Nyankole",
    "nyo": "Nyoro",
    "nzi": "Nzima",
    "oci": "Occitan (post 1500)",
    "oji": "Ojibwa",
    "ori": "Oriya",
    "orm": "Oromo",
    "osa": "Osage",
    "oss": "Ossetian",
    "ota": "Turkish",
    "oto": "Otomian",
    "paa": "Papuan",
    "pag": "Pangasinan",
    "pal": "Pahlavi",
    "pam": "Pampanga",
    "pan": "Panjabi",
    "pap": "Papiamento",
    "pau": "Palauan",
    "peo": "Persian",
    "phi": "Philippine",
    "phn": "Phoenician",
    "pli": "Pali",
    "pol": "Polish",
    "pon": "Pohnpeian",
    "por": "Portuguese",
    "pra": "Prakrit",
    "pro": "Provençal",
    "pus": "Pushto",
    "qaa-qtz": "Reserved for local use",
    "que": "Quechua",
    "raj": "Rajasthani",
    "rap": "Rapanui",
    "rar": "Rarotongan",
    "roa": "Romance",
    "roh": "Romansh",
    "rom": "Romany",
    "ron_rum": "Romanian",
    "run": "Rundi",
    "rup": "Aromanian",
    "rus": "Russian",
    "sad": "Sandawe",
    "sag": "Sango",
    "sah": "Yakut",
    "sai": "South American Indian",
    "sal": "Salishan",
    "sam": "Samaritan Aramaic",
    "san": "Sanskrit",
    "sas": "Sasak",
    "sat": "Santali",
    "scn": "Sicilian",
    "sco": "Scots",
    "sel": "Selkup",
    "sem": "Semitic",
    "sga": "Irish",
    "sgn": "Sign",
    "shn": "Shan",
    "sid": "Sidamo",
    "sin": "Sinhala",
    "sio": "Siouan",
    "sit": "Sino-Tibetan",
    "sla": "Slavic",
    "slk_slo": "Slovak",
    "slv": "Slovenian",
    "sma": "Southern Sami",
    "sme": "Northern Sami",
    "smi": "Sami",
    "smj": "Lule Sami",
    "smn": "Inari Sami",
    "smo": "Samoan",
    "sms": "Skolt Sami",
    "sna": "Shona",
    "snd": "Sindhi",
    "snk": "Soninke",
    "sog": "Sogdian",
    "som": "Somali",
    "son": "Songhai",
    "sot": "Sotho",
    "spa": "Spanish",
    "sqi_alb": "Albanian",
    "srd": "Sardinian",
    "srn": "Sranan Tongo",
    "srp": "Serbian",
    "srr": "Serer",
    "ssa": "Nilo-Saharan",
    "ssw": "Swati",
    "suk": "Sukuma",
    "sun": "Sundanese",
    "sus": "Susu",
    "sux": "Sumerian",
    "swa": "Swahili",
    "swe": "Swedish",
    "syc": "Classical Syriac",
    "syr": "Syriac",
    "tah": "Tahitian",
    "tai": "Tai",
    "tam": "Tamil",
    "tat": "Tatar",
    "tel": "Telugu",
    "tem": "Timne",
    "ter": "Tereno",
    "tet": "Tetum",
    "tgk": "Tajik",
    "tgl": "Tagalog",
    "tha": "Thai",
    "tig": "Tigre",
    "tir": "Tigrinya",
    "tiv": "Tiv",
    "tkl": "Tokelau",
    "tlh": "Klingon",
    "tli": "Tlingit",
    "tmh": "Tamashek",
    "tog": "Tonga (Nyasa)",
    "ton": "Tonga (Tonga Islands)",
    "tpi": "Tok Pisin",
    "tsi": "Tsimshian",
    "tsn": "Tswana",
    "tso": "Tsonga",
    "tuk": "Turkmen",
    "tum": "Tumbuka",
    "tup": "Tupi",
    "tur": "Turkish",
    "tut": "Altaic",
    "tvl": "Tuvalu",
    "twi": "Twi",
    "tyv": "Tuvinian",
    "udm": "Udmurt",
    "uga": "Ugaritic",
    "uig": "Uighur",
    "ukr": "Ukrainian",
    "umb": "Umbundu",
    "und": "Undetermined",
    "urd": "Urdu",
    "uzb": "Uzbek",
    "vai": "Vai",
    "ven": "Venda",
    "vie": "Vietnamese",
    "vol": "Volapük",
    "vot": "Votic",
    "wak": "Wakashan",
    "wal": "Wolaitta",
    "war": "Waray",
    "was": "Washo",
    "wen": "Sorbian",
    "wln": "Walloon",
    "wol": "Wolof",
    "xal": "Kalmyk",
    "xho": "Xhosa",
    "yao": "Yao",
    "yap": "Yapese",
    "yid": "Yiddish",
    "yor": "Yoruba",
    "ypk": "Yupik",
    "zap": "Zapotec",
    "zbl": "Blissymbols",
    "zen": "Zenaga",
    "zgh": "Standard Moroccan Tamazight",
    "zha": "Zhuang",
    "zho_chi": "Chinese",
    "znd": "Zande",
    "zul": "Zulu",
    "zun": "Zuni",
    "zxx": "No linguistic content",
    "zza": "Zaza"
}


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
    if not force and len([c for c in word if c.isalpha() and c.isupper()]) >= 2:
        # If the word already has 2 upper case letters, we wont do anything for it and we'll leave it unchanged
        return word
    lower_word = word.lower()
    if _roman.match(lower_word) is not None:
        return word.upper()
    if not articles and lower_word in _articles:
        return lower_word
    return re.sub(
        r"[A-Za-z]+('[A-Za-z]+)?",
        lambda w: w.group(0).capitalize(),
        word
    )


def _normalize(string):
    return ''.join([c.lower() for c in string if _isalphanum(c)])


def name(string):
    """
    :param string: to convert to proper case
    :return: author name capitalized
    """
    words = [_capitalize(w, force=True) for w in string.split(' ')]
    return ' '.join(words)


def title(string):
    """
    :param string: to convert to proper case
    :return: book title capitalized
    """
    words = string.split(' ')
    first = [_capitalize(words[0], articles=True)]
    words = [_capitalize(w) for w in words[1:]]
    return ' '.join(first + words)


def ordering_name(string):
    """
    :param string: name of an author to normalize and order
    :return: string containing the author name in normalized form removing any honorifics or roman numerals from the name and
    starting from the first last name
    """
    words = [w for w in _normalize(string).split(' ') if w not in _honorifics and _roman.match(w) is None]
    # words.append(words.pop(0))
    return ' '.join(words)


def ordering_title(string):
    """
    :param string: title of the book to normalize and order
    :return: string containing the title name in normalized form removing any articles that may lead the title
    """
    words = []
    first_found = False
    for w in _normalize(string).split(' '):
        if w not in _articles and not first_found:
            first_found = True
        if first_found:
            words.append(w)
    return ' '.join(words)


def sha56(string):
    return hashlib.sha256(_normalize(string).encode('utf-8')).hexdigest().upper()


def is_num(string):
    """
    :param string: to validate for only numeric values
    :return: True if all characters in the string are numeric, False otherwise
    """
    for char in string:
        if not char.isdigit():
            return False
    return True


def match_lang(string):
    if len(string) < 2:
        return None
    string = _normalize(string)
    if string in _iso_639_2:
        return string
    for k in _iso_639_2:
        if k.startswith(string) or ('_' in k and k.split('_')[1].startswith(string)):
            return k
    return None


def desc_lang(string):
    if string in _iso_639_2:
        return f"{_iso_639_2[string]} ({string})"
    return 'Unknown'


def get_langs():
    return {i[0]: i[1] for i in sorted(_iso_639_2.items(), key=lambda x: x[1])}
