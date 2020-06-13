from .constants import punktuation_mark_re, direct_speech_re, SSP
from .utils import SentenceAnalyzer
from typing import List
from nltk import sent_tokenize, word_tokenize
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
    is_exclamative: bool
    is_interrogative: bool
    words: List[Word]

    def __init__(self, text: str):
        self.text = text
        self.words = []
        self.__guess_punctuation()
        self.__parse_words()
        self.syllable_count = 0
        self.symbol_count = 0
        self.average_symbol_count = .0
        self.average_syllable_count = .0
        self.__count_metrics()

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
        self.__parse()
        self.verb_to_all_ratio = .0
        self.noun_to_all_ratio = .0
        self.ad_to_all_ratio = .0
        self.sent_syl_average = .0
        self.word_average_sym_count = .0
        self.word_average_syl_count = .0
        self.exclamative_sent_word_ratio = .0
        self.interrogative_sent_word_ratio = .0
        self.len_sentence_in_symbols_average = .0
        self.total_syllables = 0
        self.one_syl_words_ratio = .0
        self.hard_words_ratio = .0
        self.smog = .0
        self.forecast = .0

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
    def sent_word_count_average(self): # sent_in_words_average_len: Average sentence length in words
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
        total_sent_syl_count = .0
        total_symbols = .0
        word_av_syl = .0
        exclamative_sum = 0
        interrogative_sum = 0
        all_words = []
        hard_words_count = 0
        flesch_sample_size = 100 if self.word_count >= 100 else self.word_count
        smog_sample_size = 30 if self.word_count >= 30 else self.word_count
        forecast_sample_size = 150 if self.word_count >= 150 else self.word_count
        total_syllables = 0
        for sent in filter(lambda s: len(s), self):
            if len(sent):
                verbs += sent.part_of_speech_count(["V"]) / len(sent)
                nouns += sent.part_of_speech_count(["S"]) / len(sent)
                ad += sent.part_of_speech_count(["A", "ADV", "ADVPRO"]) / len(sent)
                total_sent_syl_count += sent.syllable_count
                word_av_syl += sent.syllable_count
                total_symbols += sent.symbol_count
                if sent.is_exclamative:
                    exclamative_sum += len(sent)
                if sent.is_interrogative:
                    interrogative_sum += len(sent)
                for word in sent:
                    all_words.append(word)
                    total_syllables += word.length('syl')
                    if word.length('syl') > 2:
                        hard_words_count += 1

        self.total_syllables = total_syllables
        self.verb_to_all_ratio = verbs / len(self)
        self.noun_to_all_ratio = nouns / len(self)
        self.ad_to_all_ratio = ad / len(self)
        self.sent_syl_average = total_sent_syl_count / len(self)  # Average sentence length in syllables (len_sentence_in_syllables_average)
        self.word_average_sym_count = total_symbols / self.word_count  # Average word length in symbols (len_word_in_sybols_average)
        self.len_sentence_in_symbols_average = total_symbols / len(self)  # Average sentence length in symbols (len_sentence_in_symbols_average)
        self.word_average_syl_count = word_av_syl / self.word_count
        self.exclamative_sent_word_ratio = exclamative_sum / self.word_count
        self.interrogative_sent_word_ratio = interrogative_sum / self.word_count
        flesch_sampled_words = random.sample(all_words, flesch_sample_size)
        self.one_syl_words_ratio = sum(
            1 for word in flesch_sampled_words if word.length('syl') == 1) / flesch_sample_size
        self.hard_words_ratio = hard_words_count / self.word_count
        smog_sampled_words = random.sample(all_words, smog_sample_size)
        self.smog = 3 + math.sqrt(sum(1 for word in smog_sampled_words if word.length('syl') > 2))
        forecast_sampled_words = random.sample(all_words, forecast_sample_size)
        self.forecast = 20 - (sum(1 for word in forecast_sampled_words if word.length('syl') == 1) / 10)

    @property
    def flesch(self):
        return 206.835 - 1.015 * (self.word_count / len(self)) - 84.6 * (self.total_syllables / self.word_count)

    @property
    def gunning_fog(self):
        return 0.4 * (self.sent_word_count_average + self.hard_words_ratio)
