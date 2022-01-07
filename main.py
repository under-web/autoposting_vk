import sqlite3
import time
import requests
import vk_api
from bs4 import BeautifulSoup
from sqlite3 import Error
from config import login, password

URL = 'https://topmemas.top/'

def post_wall_vk(name_image):
    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()

    vk = vk_session.get_api()
    upload = vk_api.VkUpload(vk)

    photo_wall = upload.photo_wall(photos=f'{name_image}', user_id=524647441)
    owner_id = 524647441
    media_id = str(photo_wall[0]['id'])
    attachments = 'photo' + str(owner_id) + '_' + media_id


    vk_session.method("wall.post", {
        'owner_id': owner_id,
        'message': 'Meme is time=)',
        'attachment': attachments,
    })


def get_request_html(url):
    res = requests.get(url).text
    return res

def get_id():
    soup_id = BeautifulSoup(get_request_html(URL), 'lxml').find_all('div', class_='cont_item')
    result_id = soup_id[0].get('id')
    return result_id

def get_file(url):
    r = requests.get(url, stream=True)
    return r

def get_name(url):
    name = url.split('/')[-1]
    return name

def save_image(name, file_object):
    with open(name, 'bw') as f:
        for chunk in file_object.iter_content(8192):
            f.write(chunk)

def grab_top_meme(URL):
    soup_img = BeautifulSoup(get_request_html(URL), 'lxml').find_all('div', class_='content_list')
    for i in soup_img:
        result_link = i.find('img').get('src')
        return 'https://topmemas.top/' + result_link

def sql_connection(result_id):
    global con
    try:
        con = sqlite3.connect('id_database.db')  # создаем базу и коннект к ней

        cursor = con.cursor()  #  создаем курсор

        cursor.execute("""CREATE TABLE IF NOT EXISTS id_picture (id TEXT)""")  # создаем команду
        con.commit()  # комитим

        cursor.execute("SELECT * FROM id_picture WHERE id = ?", (result_id,))

        if cursor.fetchone() is None:  # если нет записи с result_id
            cursor.execute("INSERT INTO id_picture VALUES (?)", (result_id,))
            con.commit()

            target_url = grab_top_meme(URL)

            try:
                save_image(get_name(target_url), get_file(target_url))
            except Exception as saver:
                print('save error', saver)
            try:
                post_wall_vk(get_name(target_url))
                print(f'отправил сообщение {result_id}')
            except Exception as poster:
                print('post error', poster)


            time.sleep(400)
        else:
            print(f'Такая запись {result_id} уже есть')
            time.sleep(400)
    except Error:
        print(Error)
    finally:
        con.commit()
        con.close()

def main():
    while True:
        try:
            sql_connection(get_id())
            continue
        except Exception as e:
            print('Error in main func', e)
            time.sleep(60)
            continue


if __name__ == '__main__':
    main()