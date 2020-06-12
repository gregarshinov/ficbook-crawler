from .constants import punktuation_mark_re, direct_speech_re, SSP
from .utils import SentenceAnalyzer
from typing import List
from nltk import sent_tokenize, word_tokenize
from lazy_property import LazyProperty


class Word:
    syllables: List[str]
    symbols: str
    POS: str
    normal_form: str

    def __init__(self, word: str, pos: str):
        self.symbols = word
        self.syllables = SSP.tokenize(word)
        self.POS = pos

    def length(self, kind="sym"):
        if kind == 'sym':
            return len(self.symbols)
        elif kind == 'syl':
            return len(self.syllables)


DICT = {}


class Sentence:
    text: str
    is_exclamative: bool
    is_interrogative: bool
    words: List[Word]

    def __init__(self, text: str):
        self.text = text
        self.words = []
        self.__guess_punctuation()
        self.__parse_words()

    def __guess_punctuation(self):
        for name, expression in punktuation_mark_re.items():
            setattr(self, name, bool(expression.match(self.text)))

    def __parse_words(self):
        for text, pos in SentenceAnalyzer(self.text):
            if text not in DICT:
                word = Word(text.lower(), pos)
                DICT[text.lower()] = word
            else:
                word = DICT[text.lower()]
            self.words.append(word)

    def __len__(self):
        return len(self.words)

    def __iter__(self) -> Word:
        for word in self.words:
            yield word

    def __str__(self):
        return self.text

    @LazyProperty
    def syllable_count(self):
        return sum(word.length('syl') for word in self.words)

    @LazyProperty
    def average_symbol_count(self):
        return sum(word.length('sym') for word in self.words) / len(self)

    @LazyProperty
    def average_syllable_count(self):
        return sum(word.length('syl') for word in self.words) / len(self)

    def part_of_speech_count(self, pos_id: List[str]):
        return sum(1 for word in self if word.POS in pos_id)


class Text:
    sentences: List[Sentence]
    text: str

    def __init__(self, text_string: str):
        self.text = text_string
        self.sentences = []
        self.__parse()
        self.verb_to_all_ratio = .0
        self.noun_to_all_ratio = .0
        self.ad_to_all_ratio = .0
        self.sent_syl_average =.0
        self.word_average_sym_count = .0
        self.word_average_syl_count = .0
        self.exclamative_sent_word_ratio = .0
        self.interrogative_sent_word_ratio = .0

    def __parse(self):
        for sent in sent_tokenize(self.text, 'russian'):
            self.sentences.append(Sentence(sent))

    def __len__(self):
        return len(self.sentences)

    def __iter__(self) -> Sentence:
        for sent in self.sentences:
            yield sent

    @LazyProperty
    def sentence_count(self):
        return len(self)

    @property
    def sent_word_count_average(self):
        return self.word_count / len(self)

    @LazyProperty
    def word_count(self):
        return sum(len(sent) for sent in self)


    @property
    def direct_speech_word_ratio(self):
        direct_speech_occurences = []
        for sent in self:
            direct_speech_occurences.extend([Sentence(speech) for speech in direct_speech_re.findall(str(sent))])
        return sum(len(sent) for sent in direct_speech_occurences if len(sent)) / self.word_count

    def count_metrics(self):
        verbs = .0
        nouns = .0
        ad = .0
        sent_syl = .0
        word_av_sym = .0
        word_av_syl = .0
        exclamative_sum = 0
        interrogative_sum = 0
        for sent in self:
            if len(sent):
                verbs += sent.part_of_speech_count(["V"]) / len(sent)
                nouns += sent.part_of_speech_count(["S"]) / len(sent)
                ad += sent.part_of_speech_count(["A", "ADV", "ADVPRO"]) / len(sent)
                sent_syl += sent.syllable_count / len(sent)
                for word in sent:
                    word_av_sym += word.length('sym') / len(sent)
                    word_av_syl += word.length('syl') / len(sent)
                if sent.is_exclamative:
                    exclamative_sum += len(sent)
                if sent.is_interrogative:
                    interrogative_sum += len(sent)

        self.verb_to_all_ratio = verbs / len(self)
        self.noun_to_all_ratio = nouns / len(self)
        self.ad_to_all_ratio = ad / len(self)
        self.sent_syl_average = sent_syl / len(self)
        self.word_average_sym_count = word_av_sym / self.word_count
        self.word_average_syl_count = word_av_syl / self.word_count
        self.exclamative_sent_word_ratio = exclamative_sum / self.word_count
        self.interrogative_sent_word_ratio = interrogative_sum / self.word_count
