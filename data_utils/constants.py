import re

from nltk import SyllableTokenizer

EXCLAMATION_RE = re.compile(r'!+')
INTERROGATION_RE = re.compile(r'\?+')

DIRECT_SPEECH_RE = re.compile(r':?\s?[–\-«\"](\s?[А-Я].+?)(?:[\-,.?!»\"]|\.\.\.)', re.DOTALL)

RUSSIAN_SONORITY_HIERARCHY = [
    "уеыаоэёюияь",  # vowels.
    "мн",  # nasals.
    "фвсзшщхцчж",  # fricatives.
    "лй",  # approximant
    "пбтдкгр",  # stops.
]
SSP = SyllableTokenizer('ru', sonority_hierarchy=RUSSIAN_SONORITY_HIERARCHY)