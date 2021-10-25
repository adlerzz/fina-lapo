NO_UNICODE = 'cp1251'
UNICODE = 'utf_16_be'

TRANSLIT_MAP = {
    "а": "a", "б": "b", "в": "v",
    "г": "g", "д": "d", "е": "ye",
    "ё": "yo", "ж": "zh", "з": "z",
    "и": "i", "й": "yy", "к": "k",
    "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "yi", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
    "А": "A", "Б": "B", "В": "V",
    "Г": "G", "Д": "D", "Е": "Ye",
    "Ё": "Yo", "Ж": "Zh", "З": "Z",
    "И": "I", "Й": "Yy", "К": "K",
    "Л": "L", "М": "M", "Н": "N",
    "О": "O", "П": "P", "Р": "R",
    "С": "S", "Т": "T", "У": "U",
    "Ф": "F", "Х": "Kh", "Ц": "Ts",
    "Ч": "Ch", "Ш": "Sh", "Щ": "Sch",
    "Ъ": "", "Ы": "Yi", "Ь": "",
    "Э": "E", "Ю": "Yu", "Я": "Ya"}

TRANSLIT = str.maketrans(TRANSLIT_MAP)


def translate_name(s):
    return s.strip()\
        .replace(' ', '_')\
        .translate(TRANSLIT)


def translate_uname(u):
    s = u.decode(UNICODE)
    t = translate_name(s)
    return bytes(t, UNICODE)