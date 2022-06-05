import requests
import json
import pandas

"""
Парсер wildberries для получения адресов и координат всех пунктов выдачи заказов
На выбор(указать в функции main):
    Россия www.wildberries.ru
    Казахстан kz.wildberries.ru
    Узбекистан uz.wildberries.ru
    Киргизия: kg.wildberries.ru
    Армения: am.wildberries.ru
    Беларусь: www.wildberries.by
    Израиль: wildberries.co.il
По всем возникшим вопросам, можете писать в группу https://vk.com/happython
Ссылка на статью: https://vk.com/@happython-sbor-koordinat-punktov-vydachi-zakazov-wildberries
Отзывы, предложения, советы приветствуются.
"""


def get_coord(domen):
    """полечение координат и id точек выдачи"""
    url = f'https://{domen}/webapi/spa/modules/pickups'
    headers = {'User-Agent': "Mozilla/5.0", 'content-type': "application/json", 'x-requested-with': 'XMLHttpRequest'}
    r = requests.get(url, headers=headers)
    data = r.json()
    # """сохраняем id  с координатами  в json"""
    # with open('wild_points_coord.json', 'w', encoding='UTF-8') as file:
    #     json.dump(data, file, indent=2, ensure_ascii=False)
    #     print(f'Данные сохранены в wild_points_coord.json')
    data_list = []
    for d in data['value']['pickups']:
        id = d['id']
        coordinates = d['coordinates']
        data_list.append({
            'id': int(id),
            'coordinates': coordinates
        })
    print("[INFO] координаты точек выдачи получены")
    return data_list


def get_points(payload: list, domen: str):
    """получаем id, адрес и описание пункта выдачи"""
    url = f"https://{domen}/webapi/poo/byids"
    # payload = "[822,978,1091]
    payload = f'{payload}'
    headers = {'User-Agent': "Mozilla/5.0", 'content-type': "application/json"}

    response = requests.post(url, data=payload, headers=headers)
    data = response.json()
    # print(data)
    # """сохраняем точки выдачи в json"""
    # with open('wild_points.json', 'w', encoding='UTF-8') as file:
    #     json.dump(data, file, indent=2, ensure_ascii=False)
    #     print(f'Данные сохранены в wild_points.json')
    data_points_list = []
    for d in data['value']:
        address = data['value'][d]['address']
        wayinfo = data['value'][d]['wayInfo']
        data_points_list.append({
            'id': int(d),
            'address': address,
            'wayInfo': wayinfo.replace('\n', ' ')
        })

        # print(f'id: {d}\nАдресс: {address}\nОписание:\n{wayinfo}\n')
    print("[INFO] id, адрес и описания точек выдачи получены")
    return data_points_list


def merge_data(data1: list, data2: list):
    """обьединение таблиц с помощью датафреймов"""
    df1 = pandas.DataFrame(data1)
    df2 = pandas.DataFrame(data2)

    df = pandas.merge(df1, df2, how='left', left_on='id', right_on="id")

    writer = pandas.ExcelWriter('wb_points.xlsx', engine='xlsxwriter')
    df.to_excel(writer, 'data')
    writer.save()
    print(f'[INFO] Данные объедены и сохранены в wb_points.xlsx\n'
          f'[INFO] Количество найденных пунктов выдачи:{len(df)}\n'
          f'Работа парсера завершена')

# def save_excel(data: list, filename: str):
#     """сохранение собранных данных в эксель файл - НЕ АКТУАЛЬНО"""
#     dataframe = pandas.DataFrame(data)
#     writer = pandas.ExcelWriter(f'{filename}.xlsx', engine='xlsxwriter')  # pip install xlsxwriter
#     dataframe.to_excel(writer, 'data')
#     writer.save()
#     print(f'Данные сохранены в файл "{filename}.xlsx"')


# def merge_tables():
#     """обьединение таблиц с помощью файлов эксель - НЕ АКТУАЛЬНО"""
#     file1 = pandas.read_excel(f'points.xlsx', sheet_name='data')
#     data1 = pandas.DataFrame(file1)
#     file2 = pandas.read_excel(f'coords.xlsx', sheet_name='data')
#     data2 = pandas.DataFrame(file2)
#     df = pandas.merge(data1, data2, how='left', left_on='id', right_on="id")
#     df = df.drop(['Unnamed: 0_x', 'Unnamed: 0_y'], axis=1)
#     writer = pandas.ExcelWriter('merge_data.xlsx')
#     df.to_excel(writer, 'data', index_label=False, index=False)
#     writer.save()
#     print('Все сохранено в merge_data.xlsx')


def main(domen):
    """получаем все координаты и id пунктов выдачи"""
    data_list_coords = get_coord(domen=domen)

    """запишем все id для отправки запроса адресов точек выдачи"""
    payload_generator = [i['id'] for i in data_list_coords]

    """получаем адреса и описание пунтов выдачи"""
    data_list_points = get_points(payload=payload_generator, domen=domen)

    """соединяем полеченные данные в эксель файл"""
    merge_data(data1=data_list_points, data2=data_list_coords)


if __name__ == '__main__':
    main('www.wildberries.ru')
    # возможные домены:
    # Россия www.wildberries.ru
    # Казахстан kz.wildberries.ru
    # Узбекистан uz.wildberries.ru
    # Киргизия: kg.wildberries.ru
    # Армения: am.wildberries.ru
    # Беларусь: www.wildberries.by
    # Израиль: wildberries.co.il


    # """НЕ АКТУАЛЬНО (сохранение файлов эксель, с последующим объединением)"""
    # """запись в эксель id, address и описание точки выдачи"""
    # save_excel(data_list_points, 'points')
    # """запись в эксель id, coordinates точек выдачи"""
    # save_excel(data_list_coords[0], 'coords')  # в скобках 0 элемент, так как функция возвращает 2 списка
    # """сохраняем спомощью объединения файлов"""
    # merge_tables()  # объединение таблиц по id








