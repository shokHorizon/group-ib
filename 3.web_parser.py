import json
import threading

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def visit_pages(pages_iter, results):
    while(True):
        try:
            page = next(pages_iter)
            res = requests.get(page)

            soup = BeautifulSoup(res.text, 'html.parser')

            data = {
                'name': soup.find('h1', class_='Fd93Bb').span.text,
                'url': page,
                'author': soup.find('div', class_='Vbfug auoIOc').a.span.text,
                'category': page.split('/')[-2],
                'description': soup.find('div', class_='bARER').text,
            }

            mid_rating = soup.find('div', class_='TT9eCd')
            rating_amount = soup.find('div', class_='EHUI5b')
            last_update = soup.find('div', class_='xg1aie')

            if mid_rating:
                data['mid_rating'] = mid_rating.text
            if rating_amount:
                data['rating_amount'] = rating_amount.text.split(';')[0]
            if last_update:
                data['last_update'] = last_update.text

            results.append(data)

        except StopIteration:
            break
    return


def main():
    ua = UserAgent()
    headers = {'User-Agent': ua.google}
    session = requests.Session()

    name = input('Введите название:').lower()
    r = session.get(f'https://play.google.com/store/search?q={name}', headers=headers)

    soup = BeautifulSoup(r.text, 'html.parser')
    pages_to_visit = [f'https://play.google.com{app["href"]}' for app in soup.find_all('a', class_='Si6A0c Gy4nib') if name in app.find('span', class_='DdYX5').text.lower()]
    print(*pages_to_visit, sep='\n')

    pages_to_visit_iter = iter(pages_to_visit)
    result_list = list()
    workers = list()

    #Запуск оптимального количества потоков
    while(not workers or len(pages_to_visit)//len(workers) > 16 and len(workers) < 16):
        t = threading.Thread(
            target=visit_pages,
            args=[
                pages_to_visit_iter,
                result_list
                ]
            )
        t.start()
        workers.append(t)

    for worker in workers:
        worker.join()

    print(json.dumps(result_list, ensure_ascii=False, indent=4))

if __name__ == '__main__':
    main()
