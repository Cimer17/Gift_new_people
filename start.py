import requests
import sqlite3
import time
import configparser

config = configparser.ConfigParser()
config.read("settings.ini", encoding="utf-8")
token = config["bot"]["token"]
group_id = config["bot"]["group_id"]
photo_id = config["bot"]["photo_id"]
delay = int(config["bot"]["delay"])

class DataBase():

    def __init__(self):
        self.conn = sqlite3.connect('vk_user.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def check_user(self, id):
        self.cursor.execute(f'SELECT name FROM users WHERE id = {id}')
        return self.cursor.fetchone()

    def add_user(self, info):
        self.cursor.execute('INSERT INTO users VALUES (?, ?);', info)
        self.conn.commit()
    
    def find_id(self):
        self.cursor.execute('SELECT id FROM users')
        return self.cursor.fetchall()

def get_user_info(id):
    url_info_user = f'https://api.vk.com/method/users.get?user_ids={id}&name_case=dat&access_token={token}&v=5.131'
    request = requests.get(url_info_user).json()
    name = request['response'][0]['first_name']
    return [id, name]

def get_photo_user(id):
    url_photo_user = f'https://api.vk.com/method/photos.get?owner_id={id}&rev=1&album_id=profile&access_token={token}&v=5.131'
    request = requests.get(url_photo_user).json()
    try:
        return request['response']['items'][0]['id']
    except (KeyError, IndexError):
        print('У пользователя отсутствует фотография!')
        return None

def create_comment(info_user, id_photo):
    if id_photo is None:
        id = info_user[0]
        message = f'Дарим @id{id}({info_user[1]}) Ранч Пиццу в честь дня рождения!'
        comment_url = f'https://api.vk.com/method/photos.createComment?owner_id={group_id}&from_group=1&photo_id={photo_id}&message={message}&access_token={token}&v=5.131'
    else:
        id = info_user[0]
        message = f'Дарим @id{id}({info_user[1]}) Ранч Пиццу в честь дня рождения!'
        attachments  = f'photo{id}_{id_photo}'
        comment_url = f'https://api.vk.com/method/photos.createComment?owner_id={group_id}&from_group=1&photo_id={photo_id}&attachments={attachments}&message={message}&access_token={token}&v=5.131'
    request = requests.get(comment_url).json()
    try:
        request['error']['error_msg']
        print('Поймал капчу')
        return 0
    except KeyError:
        return 1
           
def start():
    url_users_group = f'https://api.vk.com/method/groups.getMembers?group_id={group_id[1:]}&access_token={token}&v=5.131'
    request = requests.get(url_users_group).json()
    list_people = request['response']['items']
    print('Собираю данные')
    for i in list_people:
        if db.check_user(i) == None:
            info_user = get_user_info(i)
            time.sleep(5)
            id_photo = get_photo_user(i)
            time.sleep(5)
            print(f'Новый пользователь id{i}! Оставляю сообщение...')
            db.add_user(info_user)
            status = create_comment(info_user, id_photo)
            if status == 1:
                print('Сообщение успешно отправил!')
            else:
                print('Сообщение не было отправлено.')
            time.sleep(10)
        else:
            continue

if __name__ == '__main__':
        print('Запустил программу...')
        db = DataBase()
        while True:
            start()
            print(f'Сплю {delay} секунд')
            time.sleep(delay)