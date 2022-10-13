from fileinput import filename
from hashlib import md5
from itertools import count
import os
from turtle import fillcolor
import requests
from PIL import Image, ImageDraw, ImageFont
import  boto3
import hashlib

s3_bucket_name = os.environ['S3_BUCKET']
s3_path = os.environ['S3_PATH']
s3_endpoint = os.environ['S3_ENDPOINT']
s3_access_key_id = os.environ['S3_ACCESS_KEY']
s3_secret_access_key = os.environ['S3_SECRET_KEY']
s3_font_link = os.environ['S3_FONT_LINK']

font_size = 72
test_phrase = "Хреносипед"

# Скачиваем шрифт
def init_font():
    try:
        font = requests.get(s3_font_link, allow_redirects=True)
        with open('font.ttf', 'wb') as font_file:
            font_file.write(font.content)
    except Exception as err:
        print ('Ошибка при загрузке шрифта ', err)
        return False
    else:
        return True

# Создаём картинку: прозрачный png с надписью
def generate_image (text: str):
    global font_size
    try:
        font = ImageFont.truetype('font.ttf', size=font_size)
        img = Image.new('RGBA', size=(1000,1000))
        imgDraw = ImageDraw.Draw(img)
        textWidth, textHeight = imgDraw.textsize(text, font=font)
        img = img.crop(box=(0,0,textWidth,textHeight))
        imgDraw = ImageDraw.Draw(img)
        imgDraw.text((0, 0), text, font=font, fill=(185,235,254))
        img.save('result.png')
    except Exception as err:
        print ('Ошибка при создании картинки: ', err)
        return False
    else:
        return True

# Получаем MD5-хэш от входной фразы, чтобы использовать его дальше в качестве уникального имени объекта в бакете
def generate_filename (text: str):
    return (hashlib.md5(bytes(text,'UTF-8')).hexdigest() + '.png')

# Загружаем файл картинки в бакет
def upload_to_bucket (filename: str):
    try:
        s3_client.upload_file(
            'result.png', 
            s3_bucket_name, 
            (s3_path + filename),
            ExtraArgs={'ACL': 'public-read'}
        )
    except Exception as err:
        print ('Ошибка загрузки в бакет: ', err)
        return False
    return True

# Проверяем, нет ли такого файла в бакете, чтобы не выполнять генерацию картинки повторно и сэкономить на объёме бакета
def file_already_in_bucket (filename):
    return bool(s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix=(s3_path + filename)).get('KeyCount'))

# основная работа здесь
def imagizer (text: str):
    filename = generate_filename(text)
    file_already_in_bucket = bool(s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix=(s3_path + filename)).get('KeyCount'))
    if not file_already_in_bucket:
        if generate_image (text):
            upload_to_bucket (filename)

def get_image_url (text: str):
    filename = generate_filename(text)
    file_already_in_bucket = bool(s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix=(s3_path + filename)).get('KeyCount'))
    if file_already_in_bucket:
        return ('http://' + s3_bucket_name + '.hb.bizmrg.com/' + s3_path + filename)



# Предстартовая инициализация    
#######
# Загружаем шрифт
if not init_font(): 
    exit (1)
# Проверяем достпность бакета
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_access_key_id,
        aws_secret_access_key=s3_secret_access_key,
        endpoint_url=s3_endpoint
        )
    result = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix=(s3_path))
except Exception as err:
    print ('Ошибка при проверке бакета ', s3_bucket_name, err)
    exit(1)

imagizer(test_phrase)
print(get_image_url(test_phrase))