from fileinput import filename
from hashlib import md5
from itertools import count
import os
import sys
from pydantic import BaseModel
from turtle import fillcolor
import requests
from PIL import Image, ImageDraw, ImageFont
# import  boto3
import asyncio
import aioboto3
import hashlib
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics

s3_bucket_name = os.environ['S3_BUCKET']
s3_path = os.environ['S3_PATH']
s3_endpoint = os.environ['S3_ENDPOINT']
s3_access_key_id = os.environ['S3_ACCESS_KEY']
s3_secret_access_key = os.environ['S3_SECRET_KEY']
s3_font_link = os.environ['S3_FONT_LINK']

font_size = 72
test_phrase = "Хреносипед"

system_is_ready = False

# API
#######
class Request(BaseModel):
    phrase: str

# Создаём API-интерфейс
app = FastAPI(
    openapi_url = "/api/imagizer/openapi.json",
    docs_url="/api/imagizer/docs"
)
# Разрешаем обращение к API с любых доменов
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    PrometheusMiddleware,
    app_name="imagizer",
    prefix='imagizer',
    labels={
        "server_name": os.getenv("HOSTNAME"),
    },
    group_paths=True,
    skip_paths=[
        '/api/healthz',
        '/metrics'],
    always_use_int_status=False
    )
app.add_route("/metrics", handle_metrics)




# Функции
#################
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

async def init_s3 ():
    global system_is_ready
    await file_already_in_bucket (s3_path)
    system_is_ready = True

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
async def upload_to_bucket (filename: str):
    global system_is_ready
    try:
        async with aioboto3.client(
                's3',
                aws_access_key_id=s3_access_key_id,
                aws_secret_access_key=s3_secret_access_key,
                endpoint_url=s3_endpoint
            ) as s3_client:
            await s3_client.upload_file(
                'result.png', 
                s3_bucket_name, 
                (s3_path + filename),
                ExtraArgs={'ACL': 'public-read'}
            )
    except Exception as err:
        print ('Ошибка загрузки в бакет: ', err)
        system_is_ready = False
        return False
    else: return True

# Проверяем, нет ли такого файла в бакете, чтобы не выполнять генерацию картинки повторно и сэкономить на объёме бакета
async def file_already_in_bucket (filename):
        session = aioboto3.Session()
        try:
            async with session.client(
                's3',
                aws_access_key_id=s3_access_key_id,
                aws_secret_access_key=s3_secret_access_key,
                endpoint_url=s3_endpoint
            ) as s3_client:
                content = await s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix=(s3_path + filename))
                return bool(content.get('KeyCount'))
        except Exception as err:
            print ('Ошибка при доступе к бакету ', s3_bucket_name, err)
            sys.exit(1)


# основная работа здесь
def imagizer (text: str):
    filename = generate_filename(text)
    if not file_already_in_bucket(text):
        if generate_image (text):
            upload_to_bucket (filename)

@app.get("/api/getimageurl/", status_code=200)
async def get_image_url (request: Request, response: Response):
    filename = generate_filename(request.phrase)
    if await file_already_in_bucket(filename):
        return {'data': ('http://' + s3_bucket_name + '.hb.bizmrg.com/' + s3_path + filename)}
    else:
        response.status_code = status.HTTP_204_NO_CONTENT
        return {'data': ''}

# readinessProbe для Кубернетес
@app.get("/api/healthz/")
async def get_history(response: Response):
    global system_is_ready
    if system_is_ready:
        response.status_code = status.HTTP_200_OK
        return
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return


# Предстартовая инициализация    
#######
# Загружаем шрифт
if not init_font(): 
    sys.exit(1)
asyncio.create_task (init_s3())
