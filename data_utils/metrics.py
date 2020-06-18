from .constants import DIRECT_SPEECH_RE, SSP, EXCLAMATION_RE, INTERROGATION_RE
from .utils import SentenceAnalyzer
from typing import List
from nltk import sent_tokenize
from lazy_property import LazyProperty
import random
import math


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
    words: List[Word]

    def __init__(self, text: str):
        self.text = text
        self.words = []
        self.__parse_words()
        self.syllable_count = 0
        self.symbol_count = 0
        self.average_symbol_count = .0
        self.average_syllable_count = .0
        self.__count_metrics()

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

    def part_of_speech_count(self, pos_id: List[str]):
        return sum(1 for word in self if word.POS in pos_id)

    def __count_metrics(self):
        syllables = 0
        symbol_count = 0
        for word in self:
            syllables += word.length('syl')
            symbol_count += word.length('sym')

        self.syllable_count = syllables
        self.symbol_count = symbol_count
        if len(self):
            self.average_syllable_count = syllables / len(self)
            self.average_symbol_count = symbol_count / len(self)


class Text:
    sentences: List[Sentence]
    text: str

    def __init__(self, text_string: str):
        self.text = text_string
        self.sentences = []
        self.words = []
        self.__parse()
        self.total_words = 0
        self.total_symbols = 0
        self.total_syllables = 0

        self.total_verbs = 0
        self.total_nouns = 0
        self.total_ad = 0

        self.total_exclamative = 0
        self.total_interrogative = 0

        self.total_hard_words = 0

        self.flesch_sample_size = 100 if self.word_count >= 100 else self.word_count
        self.smog_sample_size = 30 if self.word_count >= 30 else self.word_count
        self.forecast_sample_size = 150 if self.word_count >= 150 else self.word_count

    def __parse(self):
        for sent in sent_tokenize(self.text, 'russian'):
            self.sentences.append(Sentence(sent))

    def __len__(self):
        return len(self.sentences)

    def __iter__(self) -> Sentence:
        for sent in self.sentences:
            yield sent

    @LazyProperty
    def word_count(self):
        return sum(len(sent) for sent in self)

    @property
    def direct_speech_word_ratio(self):
        direct_speech_occurences = []
        for sent in self:
            direct_speech_occurences.extend([Sentence(speech) for speech in DIRECT_SPEECH_RE.findall(str(sent))])
        return sum(len(sent) for sent in direct_speech_occurences if len(sent)) / self.word_count

    def count_metrics(self):
        for sent in filter(lambda s: len(s), self):
            self.total_verbs += sent.part_of_speech_count(["V"])
            self.total_nouns += sent.part_of_speech_count(["S"])
            self.total_ad += sent.part_of_speech_count(["A", "ADV", "ADVPRO"])
            self.total_syllables += sent.syllable_count
            self.total_symbols += sent.symbol_count
            for word in sent:
                self.words.append(word)
                if word.length('syl') > 2:
                    self.total_hard_words += 1


    @property
    def sent_in_words_average_len(self):
        return self.word_count / len(self)

    @property
    def sent_in_syl_average_len(self):
        return self.total_syllables / len(self)

    @property
    def sent_sym_average_len(self):
        return self.total_symbols / len(self)

    @property
    def word_in_sym_average_len(self):
        return self.total_symbols / self.word_count

    @property
    def word_in_syl_average_len(self):
        return self.total_syllables / self.word_count

    @property
    def verb_to_all_ratio(self):
        return self.total_verbs / self.word_count

    @property
    def noun_to_all_ratio(self):
        return self.total_nouns / self.word_count

    @property
    def ad_to_all_ratio(self):
        return self.total_ad / self.word_count

    @property
    def interrogative_sent_word_ratio(self):
        return len(INTERROGATION_RE.findall(self.text)) / len(self)

    @property
    def exclamative_sent_word_ratio(self):
        return len(EXCLAMATION_RE.findall(self.text)) / len(self)

    @property
    def smog(self):
        smog_sampled_words = random.sample(self.words, self.smog_sample_size)
        return 3 + math.sqrt(sum(1 for word in smog_sampled_words if word.length('syl') > 2))

    @property
    def forecast(self):
        forecast_sampled_words = random.sample(self.words, self.forecast_sample_size)
        return 20 - (sum(1 for word in forecast_sampled_words if word.length('syl') == 1) / 10)

    @property
    def flesch(self):
        return 206.835 - 1.015 * (self.word_count / len(self)) - 84.6 * (self.total_syllables / self.word_count)

    @property
    def gunning_fog(self):
        return 0.4 * (self.sent_in_words_average_len + self.total_hard_words / self.word_count)
