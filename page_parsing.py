from settings import BASE_URL, ORIGINALS_URL
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import dateparser


def fetch_catalogue_page(idx: int = None) -> str:
    if not idx:
        response = requests.get(BASE_URL + ORIGINALS_URL)
    else:
        response = requests.get(BASE_URL + ORIGINALS_URL, params={'p': idx})

    return response.content.decode()


def get_readlinks(page_html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(page_html, features="lxml")
    elements = soup.find_all(href=re.compile("/readfic/\d+"))
    return [{'title': e.text, 'url': BASE_URL + e.attrs['href']} for e in elements]


def get_dd(search_term: str, soup: BeautifulSoup) -> str:
    els = soup.find_all('dt', text=search_term, limit=1)
    if els:
        el = els[0].find_all_next('dd', limit=1)[0]  # type: BeautifulSoup
    else:
        return ''
    text = getattr(el.strong or el.span, 'text', None)
    return text


def get_dates(soup: BeautifulSoup) -> Dict[str, datetime]:
    date_els = soup.find_all('span', title=re.compile(r'\d{2}\s\w+\s\d{4}'))
    dates = sorted([dateparser.parse(date_el['title']) for date_el in date_els])
    if dates:
        return {"date_added": dates[0], "last_updated": dates[-1]}
    else:
        return {"date_added": datetime.today(), "last_updated": datetime.today()}


def get_fic_text(soup: BeautifulSoup):
    parts = []
    if soup.find('h2', text='Содержание'):
        part_link_els = soup.find_all('a', href=re.compile(r'/readfic/\d+/\d+#part_content'))
        for link_el in part_link_els:
            response = requests.get(BASE_URL + link_el.attrs["href"])
            part_soup = BeautifulSoup(response.content, features="lxml")
            parts.append(getattr(part_soup.select_one('article > div#content'), 'text', ''))
    else:
        parts.append(getattr(soup.select_one('article > div#content'), 'text', ''))
    return parts


def parse_fic(page_html):
    soup = BeautifulSoup(page_html, features="lxml")
    likes = getattr(soup.select_one("span.js-marks-plus"), 'text', '')
    pairing = getattr(soup.find("a", href=re.compile(r'/pairings/.+')), 'text', '')
    rating = get_dd('Рейтинг:', soup)
    size = get_dd('Размер:', soup)
    status = get_dd('Статус:', soup)
    if tags_el := soup.select_one('dd.tags'):
        tags = [el.text for el in tags_el.find_all('a')]
    else:
        tags = []
    author = soup.select_one('div.creator-info > a').text
    author_notes = ''
    if author_notes_el := soup.find('strong', text='Примечания автора:'):
        author_notes = author_notes_el.find_all_next('div', limit=1)[0].text
    description = ''
    if description_el := soup.find('strong', text='Описание:'):
        description = description_el.find_all_next('div', limit=1)[0].text

    text = "\n".join(get_fic_text(soup))
    dates = get_dates(soup)

    return {'like_count': likes.strip('\n '),
            'pairing_and_characters': pairing.strip('\n '),
            'rating': rating.strip('\n '),
            'size': size.strip('\n '),
            'status': status.strip('\n '),
            'tags': '|'.join(tags),
            'author_notes': author_notes.strip('\n '),
            'description': description.strip('\n '),
            'author': author,
            'text': text,
            'date_added': dates['date_added'],
            'last_updated': dates['last_updated']}
