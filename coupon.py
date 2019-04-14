import pyqrcode
from PIL import Image
from multiprocessing import Process, Queue
import base64
import io
import vk_api
from vk_api import VkUpload
import requests
from random import randint
from os import remove


def code_img(filename):
    msg = b"<plain_txt_msg:img>"
    with open(filename, "rb") as imageFile:
        msg = msg + base64.b64encode(imageFile.read())
    msg = msg + b"<!plain_txt_msg>"
    return msg


def decode_img(msg):
    msg = msg[msg.find(b"<plain_txt_msg:img>") + len(b"<plain_txt_msg:img>"):
              msg.find(b"<!plain_txt_msg>")]
    msg = base64.b64decode(msg)
    buf = io.BytesIO(msg)
    img = Image.open(buf)
    return img


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
            coupon.save('coupon.png')
            self.q.put(code_img('coupon.png'))


class Sender(object):
    def __init__(self, q):
        self.q = q

    def vk(self):
        while True:
            vk_session = vk_api.VkApi('***', '***')
            vk_session.auth(token_only=True)
            upload = vk_api.VkUpload(vk_session)
            vk = vk_session.get_api()
            decode_img(self.q.get()).save('post.png')
            photo = upload.photo('post.png', album_id=262366816, group_id=181149880)
            photos = '{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])
            url = vk.photos.getById(photos=photos, extends=0)[0]['sizes'][6]['url']
            remove('post.png')
            vk_session = vk_api.VkApi(
                token='*****')
            vk = vk_session.get_api()
            attachments = []
            upload = VkUpload(vk_session)
            session = requests.Session()
            image = session.get(url, stream=True)
            photo = upload.photo_messages(photos=image.raw)[0]
            attachments.append(
                'photo{}_{}'.format(photo['owner_id'], photo['id'])
            )

            vk.messages.send(
                user_id=***,
                attachment=','.join(attachments),
                message='Ваш код готов!',
                random_id=randint(1, 999999)
            )


if __name__ == '__main__':
    q = Queue()
    produce = Produce(q)
    sender = Sender(q)

    for _ in range(2):
        produce_process = Process(target=produce.coupon, args=())
        produce_process.start()

    sender_process = Process(target=sender.vk, args=())
    sender_process.start()
