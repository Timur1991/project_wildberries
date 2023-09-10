import json


with open('NEW_wb_points.json', 'r', encoding='UTF-8') as file:
    data = json.load(file)

for d in data:
    print(f'ID:{d["id"]} Рейтинг: {d["rate"]}\nАдресс: {d["address"]}\n')