from pathlib import Path
import re
from db.session_manager import session_scope
from db.models import Novel
from collections import Counter
import pickle


def parse_tag_file():
    raw_tag_file = Path('statistics').joinpath('genres.txt')
    with raw_tag_file.open() as file:
        genres_raw = file.read()

    for genre_str in genres_raw.split("\n\n\n\n"):
        genres = [re.search(r'(?P<genre>.+):\s+(?P<subgenres>.+)\n?', genre_str, re.DOTALL)]
        for m in genres:
            print(m)


def count_tags():
    with session_scope() as session:
        novels = session.query(Novel.id, Novel.tags).all()
        tag_counter = Counter()
        for novel in novels:
            tag_counter.update(novel.tags.split("|"))
            print(novel.id)

        with open("tags.pickle", 'wb') as file:
            pickle.dump(tag_counter, file)


if __name__ == '__main__':
    count_tags()
