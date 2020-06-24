import random
import time
from typing import List

import requests
from sqlalchemy import and_

from data_utils.metrics import Text
from db.models import Novel
from db.session_manager import session_scope
from page_parsing import get_readlinks, parse_fic
from settings import BASE_URL, TIME_INTERVALS


def get_find_page(direction_id: int = 1, page: int = 1) -> str:
    params = {
        'fandom_filter': 'originals',
        'fandom_group_id': 1,
        'sizes[0]': 2,
        'sizes[1]': 3,
        'pages_min': '',
        'pages_max': '',
        'ratings[0]': 5,
        'ratings[1]': 6,
        'ratings[2]': 7,
        'ratings[3]': 8,
        'ratings[4]': 9,
        'transl': 3,
        'statuses[0]': 2,
        'directions[0]': direction_id,
        'likes_min': '',
        'likes_max': '',
        'date_create_min': '2020-05-11',
        'date_create_max': '2020-06-11',
        'date_update_min': '2020-05-11',
        'date_update_max': '2020-06-11',
        'title': '',
        'sort': 5,
        'rnd': '1641277685',
        'find': 'Найти!',
        'p': page
    }

    response = requests.get(BASE_URL + '/find', params=params)
    return response.content.decode()


def crawl_find(directions: List[int], page_range=(0, 50), max_count=500):
    count = 0
    for direction_id in directions:
        print(f"Direction: {direction_id}")
        for i in range(*page_range):
            if count <= max_count:
                print(f"Page {i}/{page_range[1]}")
                fanfic_addresses = get_readlinks(get_find_page(direction_id, i))
                with session_scope() as sess:
                    already_exist_obj = sess.query(Novel.url).filter(
                        Novel.url.in_([a['url'] for a in fanfic_addresses])).all()
                    already_exist_lst = [o.url for o in already_exist_obj]
                for idx, fic_address in enumerate(
                        [fa for fa in fanfic_addresses if fa['url'] not in already_exist_lst]):
                    if count <= max_count:
                        fic_page = requests.get(fic_address['url'])
                        result = parse_fic(fic_page.content.decode())
                        result.update(fic_address)
                        result['direction'] = direction_id
                        text = Text(result["text"])
                        if text.word_count:
                            text.count_metrics()
                            metrics = {
                                'total_words': text.word_count,
                                'total_sents': len(text),
                                'total_sym': text.total_symbols,
                                'total_syl': text.total_syllables,

                                'ad_to_all_ratio': text.ad_to_all_ratio,
                                'noun_to_all_ratio': text.noun_to_all_ratio,
                                'verb_to_all_ratio': text.verb_to_all_ratio,

                                'direct_speech_word_ratio': text.direct_speech_word_ratio,
                                'exclamative_sent_word_ratio': text.exclamative_sent_word_ratio,
                                'interrogative_sent_word_ratio': text.interrogative_sent_word_ratio,

                                'sent_sym_average_len': text.sent_sym_average_len,
                                'sent_in_syl_average_len': text.sent_in_syl_average_len,
                                'sent_in_words_average_len': text.sent_in_words_average_len,

                                'word_in_syl_average_len': text.word_in_syl_average_len,
                                'word_in_sym_average_len': text.word_in_sym_average_len,

                                'forecast': text.forecast,
                                'smog': text.smog,
                                'gunning_fog': text.gunning_fog,
                                'flesch': text.flesch
                            }
                            result.update(metrics)
                        with session_scope() as sess:
                            sess.add(Novel(**result))
                            print(f"Text {idx}")
                        count += 1
                        time.sleep(random.choice(TIME_INTERVALS))
                    else:
                        break
            else:
                count = 0
                break


def recalculate_metrics():
    with session_scope() as query_session:
        novels = query_session.query(Novel).filter(and_(Novel.text.isnot(None),
                                                        Novel.rating.isnot(None))).all()
        for novel in novels:
            print(novel.title)
            with session_scope() as session:
                text = Text(novel.text)
                if text.word_count:
                    text.count_metrics()
                    metrics = {
                        Novel.total_words: text.word_count,
                        Novel.total_sents: len(text),
                        Novel.total_sym: text.total_symbols,
                        Novel.total_syl: text.total_syllables,

                        Novel.ad_to_all_ratio: text.ad_to_all_ratio,
                        Novel.noun_to_all_ratio: text.noun_to_all_ratio,
                        Novel.verb_to_all_ratio: text.verb_to_all_ratio,

                        Novel.direct_speech_word_ratio: text.direct_speech_word_ratio,
                        Novel.exclamative_sent_word_ratio: text.exclamative_sent_word_ratio,
                        Novel.interrogative_sent_word_ratio: text.interrogative_sent_word_ratio,

                        Novel.sent_sym_average_len: text.sent_sym_average_len,
                        Novel.sent_in_syl_average_len: text.sent_in_syl_average_len,
                        Novel.sent_in_words_average_len: text.sent_in_words_average_len,

                        Novel.word_in_syl_average_len: text.word_in_syl_average_len,
                        Novel.word_in_sym_average_len: text.word_in_sym_average_len,

                        Novel.forecast: text.forecast,
                        Novel.smog: text.smog,
                        Novel.gunning_fog: text.gunning_fog,
                        Novel.flesch: text.flesch
                    }
                    session.query(Novel).filter(Novel.id == novel.id).update(metrics)
                    print("Done")
                else:
                    print("Skipping")