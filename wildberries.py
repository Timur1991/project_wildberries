import requests
from bs4 import BeautifulSoup
import pandas
from pandas import ExcelWriter
import openpyxl
import lxml


"""
парсер торговой площадки Wildberries
приношу свои извинения, но В ДАННЫЙ МОМЕНТ ПАРСЕР НЕ РАБОТАЕТ
(постараюсь реанимировать, как появится свободное время)

По всем возникшим вопросам, можете писать в группу https://vk.com/happython
"""


def get_html(url, params=None):
    """html код страницы"""
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    }
    html = requests.get(url, headers=headers, params=params)
    return html


def get_pages(html):
    """получение количества страниц"""
    soup = BeautifulSoup(html.text, 'lxml')
    try:
        good_count = soup.find('h1').find_next('span').get_text(strip=True).replace("\xa0", '').split()[0]
        pages = int(good_count) // 100 + 1
    except:
        pages = 1
    return pages


def get_content(html):
    """сбор контента со страницы"""
    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.find_all('div', class_="product-card")
    global title
    title = soup.h1.text
    cards = []
    for item in items:
        # проверка на наличии скидки, если нет, то поле пустое
        try:
            discount = item.find('span', class_='product-card__sale active')
            if discount:
                discount = discount.get_text(strip=True).replace('%', '')
            else:
                discount = item.find('span', class_='product-card__sale').get_text(strip=True).replace('%', '')
        except:
            discount = 0
        # проверка цены
        try:
            price = item.find(class_='lower-price').get_text(strip=True).replace('\xa0', '').replace('₽', '')
        except:
            price = item.find('span', class_='price-commission__current-price').get_text(strip=True).replace('\xa0',
                                                                                                             '').replace(
                '₽', '')

        cards.append({
            'brand': item.find('strong', class_='brand-name').get_text(strip=True).replace('/', ''),
            'title': item.find('span', class_='goods-name').get_text(),
            'price': int(price),
            'discount': int(discount),
            'link': f'https://www.wildberries.ru{item.find("a", class_="product-card__main").get("href")}',
        })
    return cards


def save_exel(data, file_name):
    """сохранение собранных данных"""
    dataframe = pandas.DataFrame(data)
    writer = ExcelWriter(f'{file_name}.xlsx')
    dataframe.to_excel(writer, 'data')
    writer.save()
    print(f'Данные сохранены в файл "{file_name}.xlsx"')


def parser(url):
    """основная функция"""
    print(f'Парсим данные с: "{url}"')
    html = get_html(url)
    if html.status_code == 200:
        pages = get_pages(html)
        print(f'Количество страниц: {pages}')
        cards = []
        pages = int(input('Введите количество страниц: '))
        for page in range(1, pages + 1):
            print(f'Парсинг страницы: {page}')
            html = get_html(url, params={'sort': 'popular', 'page': page})
            cards.extend(get_content(html))
        print(f'Всего: {len(cards)} позиций')
        save_exel(cards, title)
    else:
        print(f'Ответ сервера:{html.status_code}. Парсинг невозможен!')


if __name__ == "__main__":
    # parser('https://www.wildberries.ru/brands/xiaomi')
    parser('https://www.wildberries.ru/brands/xiaomi/all')
    """Примеры ссылок:"""
    # parser('https://www.wildberries.ru/catalog/sport/vidy-sporta/velosport/velosipedy')
    # parser('https://www.wildberries.ru/catalog/knigi/uchebnaya-literatura?xsubject=2076')
    # parser('https://www.wildberries.ru/catalog/knigi/uchebnaya-literatura?xsubject=3647')
    # parser('https://www.wildberries.ru/brands/birkenstock')
    """Пример формата ссылки, с которым не работает парсер:"""
    "https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%BD%D0%BE%D1%83%D1%82%D0%B1%D1%83%D0%BA&xsearch=true"
