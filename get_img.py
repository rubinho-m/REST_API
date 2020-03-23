import requests
from spn_selection import get_spn

def get_img(name):
    print(name)
    s = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={name}&format=json"
    response = requests.get(s)
    json_response = response.json()
    toponym_coodrinates = \
        json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
            "pos"]
    toponym_coodrinates = toponym_coodrinates.split()
    x, y = toponym_coodrinates[0], toponym_coodrinates[1]
    first, second = get_spn(name)

    map_request = f"https://static-maps.yandex.ru/1.x/?l=map&ll={x},{y}&spn={first},{second}"
    return map_request
    # response = requests.get(map_request)

    # Запишем полученное изображение в файл.
    # map_file = "static/img/map.png"
    # with open(map_file, "wb") as file:
    #     file.write(response.content)
