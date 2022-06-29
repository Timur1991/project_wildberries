import requests
import json
import pandas as pd


"""
Парсер wildberries по ссылке на каталог

Парсер не идеален, есть множество вариантов реализации, со своими идеями 
и предложениями обязательно пишите мне, либо в группу, ссылка ниже.

Ссылка на статью ВКонтакте: https://vk.com/@happython-parser-wildberries
По всем возникшим вопросам, можете писать в группу https://vk.com/happython
"""


def get_catalogs_wb():
    """получение каталога вб"""
    url = 'https://static.wbstatic.net/data/main-menu-ru-ru.json'
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    data = response.json()
    # with open('wb_catalogs_data.json', 'w', encoding='UTF-8') as file:
    #     json.dump(data, file, indent=2, ensure_ascii=False)
    #     print(f'Данные сохранены в wb_catalogs_data.json')
    data_list = []
    for d in data:
        try:
            for child in d['childs']:
                try:
                    category_name = child['name']
                    category_url = child['url']
                    shard = child['shard']
                    query = child['query']
                    data_list.append({
                        'category_name': category_name,
                        'category_url': category_url,
                        'shard': shard,
                        'query': query})
                except:
                    continue
                try:
                    for sub_child in child['childs']:
                        category_name = sub_child['name']
                        category_url = sub_child['url']
                        shard = sub_child['shard']
                        query = sub_child['query']
                        data_list.append({
                            'category_name': category_name,
                            'category_url': category_url,
                            'shard': shard,
                            'query': query})
                except:
                    # print(f'не имеет дочерних каталогов *{i["name"]}*')
                    continue
        except:
            # print(f'не имеет дочерних каталогов *{d["name"]}*')
            continue
    return data_list


def search_category_in_catalog(url, catalog_list):
    """пишем проверку пользовательской ссылки на наличии в каталоге"""
    try:
        for catalog in catalog_list:
            if catalog['category_url'] == url.split('https://www.wildberries.ru')[-1]:
                print(f'найдено совпадение: {catalog["category_name"]}')
                name_category = catalog['category_name']
                shard = catalog['shard']
                query = catalog['query']
                return name_category, shard, query
            else:
                # print('нет совпадения')
                pass
    except:
        print('Данный раздел не найден!')


def get_data_from_json(json_file):
    """извлекаем из json интересующие нас данные"""
    data_list = []
    for data in json_file['data']['products']:
        try:
            price = int(data["priceU"] / 100)
        except:
            price = 0
        data_list.append({
            'Наименование': data['name'],
            'id': data['id'],
            'Скидка': data['sale'],
            'Цена': price,
            'Цена со скидкой': int(data["salePriceU"] / 100),
            'Бренд': data['brand'],
            'id бренда': int(data['brandId']),
            'feedbacks': data['feedbacks'],
            'rating': data['rating'],
            'Ссылка': f'https://www.wildberries.ru/catalog/{data["id"]}/detail.aspx?targetUrl=BP'
        })
    return data_list


def get_content(shard, query, low_price=1, top_price=200000):
    # вставляем ценовые рамки для уменьшения выдачи, вилбериес отдает только 100 страниц
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    data_list = []
    for page in range(1, 101):
        print(f'Сбор позиций со страницы {page} из 100')
        url = f'https://wbxcatalog-ru.wildberries.ru/{shard}' \
              f'/catalog?appType=1&curr=rub&dest=-1029256,-102269,-1278703,-1255563' \
              f'&{query}&lang=ru&locale=ru&sort=sale&page={page}' \
              f'&priceU={low_price * 100};{top_price * 100}'
        r = requests.get(url, headers=headers)
        data = r.json()
        print(f'Добавлено позиций: {len(get_data_from_json(data))}')
        if len(get_data_from_json(data)) > 0:
            data_list.extend(get_data_from_json(data))
        else:
            print(f'Сбор данных завершен.')
            break
    return data_list


def save_excel(data, filename):
    """сохранение результата в excel файл"""
    df = pd.DataFrame(data)
    writer = pd.ExcelWriter(f'{filename}.xlsx')
    df.to_excel(writer, 'data')
    writer.save()
    print(f'Все сохранено в {filename}.xlsx')


def parser():
    # получаем список каталогов
    catalog_list = get_catalogs_wb()

    # url = input('Введите ссылку на категорию для сбора: ')
    # low_price = int(input('Введите минимальную сумму товара: '))
    # top_price = int(input('Введите максимульную сумму товара: '))

    # тестовые данные 1
    url = 'https://www.wildberries.ru/catalog/sport/vidy-sporta/velosport/velosipedy'
    low_price = 50000
    top_price = 100000

    # тестовые данные 2
    # url = 'https://www.wildberries.ru/catalog/knigi/vospitanie-i-razvitie-rebenka'
    # low_price = 1000
    # top_price = 100000

    try:
        # поиск введенной категории в общем каталоге
        name_category, shard, query = search_category_in_catalog(url=url, catalog_list=catalog_list)
        # сбор данных в найденном каталоге
        data_list = get_content(shard=shard, query=query, low_price=low_price, top_price=top_price)
        # сохранение найденных данных
        save_excel(data_list, f'{name_category}_from_{low_price}_to_{top_price}')
    except TypeError:
        print('Ошибка! Возможно не верно указан раздел. Удалите все доп фильтры с ссылки')
    except PermissionError:
        print('Ошибка! Вы забыли закрыть созданный ранее excel файл. Закройте и повторите попытку')


if __name__ == '__main__':
    parser()

