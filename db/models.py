from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float


Base = declarative_base()


class Novel(Base):
    __tablename__ = 'novel'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True)
    title = Column(String)
    author = Column(String)
    description = Column(String)
    pairing_and_characters = Column(String)
    rating = Column(String)
    size = Column(String)
    status = Column(String)
    tags = Column(String)
    author_notes = Column(String)
    like_count = Column(Integer)
    text = Column(String)
    date_added = Column(Date)
    last_updated = Column(Date)
    direction = Column(Integer)

    total_sents = Column(Integer)
    total_words = Column(Integer)
    total_syl = Column(Integer)
    total_sym = Column(Integer)

    sent_in_words_average_len = Column(Float)
    sent_in_syl_average_len = Column(Float)
    sent_sym_average_len = Column(Float)

    word_in_sym_average_len = Column(Float)
    word_in_syl_average_len = Column(Float)

    verb_to_all_ratio = Column(Float)
    noun_to_all_ratio = Column(Float)
    ad_to_all_ratio = Column(Float)

    exclamative_sent_word_ratio = Column(Float)
    interrogative_sent_word_ratio = Column(Float)
    direct_speech_word_ratio = Column(Float)

    forecast = Column(Float)
    gunning_fog = Column(Float)
    smog = Column(Float)
    flesch = Column(Float)
