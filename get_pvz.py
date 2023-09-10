import requests
import json
import pandas


def get_coord(domen):
    """полечение координат и id точек выдачи"""
    url = f'https://{domen}/webapi/spa/modules/pickups'
    headers = {'User-Agent': "Mozilla/5.0", 'content-type': "application/json", 'x-requested-with': 'XMLHttpRequest'}
    r = requests.get(url, headers=headers)
    data = r.json()
    """сохраняем id  с координатами  в json"""
    # with open('wild_points_coord.json', 'w', encoding='UTF-8') as file:
    #     json.dump(data, file, indent=4, ensure_ascii=False)
    #     print(f'Данные сохранены в wild_points_coord.json')
    data_list = []
    for d in data['value']['pickups']:
        id = d['id']
        address = d['address']
        coordinates = d['coordinates']
        workTime = d.get('workTime', '')
        data_list.append({
            'id': int(id),
            'address': address,
            'coordinates': coordinates,
            'workTime': workTime
        })
    print("[INFO] координаты точек выдачи получены")
    return data_list


def get_points(payload: list, domen: str):
    """получаем id, адрес и описание пункта выдачи"""
    url = f"https://{domen}/webapi/poo/byids"
    # payload = [7,8,9]
    payload = f'{payload}'
    headers = {'User-Agent': "Mozilla/5.0", 'content-type': "application/json"}

    response = requests.post(url, data=payload, headers=headers)
    data = response.json()
    # print(data)
    """сохраняем точки выдачи в json"""
    # with open('wild_points.json', 'w', encoding='UTF-8') as file:
    #     json.dump(data, file, indent=2, ensure_ascii=False)
    #     print(f'Данные сохранены в wild_points.json')
    data_points_list = []
    for d in data['value']:
        wayinfo = data['value'][d].get('wayInfo', '')
        rate = data['value'][d].get('rate', 0)
        data_points_list.append({
            'id': int(d),
            'rate': rate,
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
    df = df[['id', 'rate', 'address', 'workTime', 'wayInfo', 'coordinates']]

    # запись в json
    df.to_json('NEW_wb_points.json', orient='records', force_ascii=False, index=True)

    # запись в эксель
    writer = pandas.ExcelWriter('NEW_wb_points.xlsx', engine='xlsxwriter')
    df.to_excel(writer, 'data')
    writer.save()

    print(f'[INFO] Данные объедены и сохранены в wb_points.xlsx\n'
          f'[INFO] Количество найденных пунктов выдачи:{len(df)}\n'
          f'Работа парсера завершена')


def main(domen):
    """получаем все координаты и id пунктов выдачи"""
    data_list_coords = get_coord(domen=domen)

    """запишем все id для отправки запроса адресов точек выдачи"""
    payload_generator = [i['id'] for i in data_list_coords]

    """получаем адреса и описание пунтов выдачи"""
    data_list_points = get_points(payload=payload_generator, domen=domen)

    """соединяем полеченные данные в эксель файл"""
    merge_data(data1=data_list_points, data2=data_list_coords)


def main2(payload, domen):
    """получаем все координаты и id пунктов выдачи"""
    data_list_coords = get_coord(domen=domen)

    """получаем адреса и описание пунтов выдачи"""
    data_list_points = get_points(payload=payload, domen=domen)

    """соединяем полеченные данные в эксель файл"""
    merge_data(data1=data_list_points, data2=data_list_coords)


if __name__ == '__main__':
    # данные по всм пвз
    # main('www.wildberries.ru')

    # данные по заданным пвз, где payload это список id пвз которые нужны
    main2(payload=[7,8,9], domen='www.wildberries.ru')

