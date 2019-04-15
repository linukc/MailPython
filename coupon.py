import pyqrcode
from PIL import Image
from multiprocessing import Process, Queue
import base64
import io
import vk_api
from random import randint
from os import remove
import time





class Produce(object):
    def __init__(self, q):
        self.q = q

    @staticmethod
    def qr():
        qr = pyqrcode.create('https://yandex.ru')
        qr.png('qr.png', scale=11)
        return 'qr.png'

    def coupon(self):
        while True:
            qr = Image.open(self.qr())
            coupon = Image.open('template.png')
            coupon.paste(qr, (90, 100))
            path = randint(1, 999999)
            coupon.save(f'coupon{path}.png')
            self.q.put(f'coupon{path}.png')
            time.sleep(1)


class Sender(object):
    def __init__(self, q):
        self.q = q

    def vk(self):
        while True:
            #добавление в альбом
            vk_session = vk_api.VkApi('****', '****')
            vk_session.auth(token_only=True)
            upload = vk_api.VkUpload(vk_session)
            path = self.q.get()
            photo = upload.photo(path, album_id=262366816, group_id=181149880)
            remove(path)
            #отправка в личные сообщения
            vk_session = vk_api.VkApi(
                token='******')
            vk = vk_session.get_api()
            attachment_photo = 'photo'+str(photo[0].get('owner_id'))+'_'+str(photo[0].get('id'))
            print(attachment_photo)
            vk.messages.send(
                user_id=****,
                attachment=attachment_photo,
                message='Ваш купон готов!',
                random_id=randint(1, 999999)
            )
            time.sleep(2)


if __name__ == '__main__':
    q = Queue()
    produce = Produce(q)
    sender = Sender(q)

    for _ in range(1):
        produce_process = Process(target=produce.coupon, args=())
        produce_process.start()

    for _ in range(3):
        sender_process = Process(target=sender.vk, args=())
        sender_process.start()

