import re
import json
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import random
import time
from starlette_exporter import PrometheusMiddleware, handle_metrics

system_is_ready = False
regexp_pattern = "[а-яА-Яеё,. ]+"
json_path = '/var/config/example.json'

# Забираем настройки из переменных окружения
append_history_url = os.environ['HISTORY_APPEND_URL']

# Создаём свой тип данных, чтобы загружать в него данные из запроса
class Request(BaseModel):
    schema_id: int
    phrase: str

# Загрузка в память схемы из файла
def load_schemas (filepath):
    global system_is_ready
    try:
        with open(filepath) as json_file:
            schema_list = json.load(json_file)
    except Exception as err:
        system_is_ready = False
        print('Cannot load schemas file', err)
    else:
        system_is_ready = True
        return schema_list['schemas']

def figalize (word,substitutions_list):
    # Создаём пустые переменные
    all_keys = ''
    current_position = 0
    found_keys = 0
    # Проверяем, сколько слогов по ключевым гласным у нас в слове
    for sub in substitutions_list:
        all_keys += sub['keys']
    # Для слов, оканчивающихся на 'ая', всегда меняем только первый слог - эмпирически, так прикольнее
    if word[-2:] == 'ая' or word[-3:] == 'ая,' or word[-3:] == 'ая.':
        replacement_step = 1
    # Если слогов меньше 3, то будем заменять первый слог, иначе некрасиво
    elif len([i for i in list(word) if i in set(all_keys)]) <= 2:
        replacement_step = 1
    # Для длинных слов с количеством слогов от 3 - меняем первые два слога
    else:
        replacement_step = 2
    for letter in word:
        current_position += 1
        for substitution in substitutions_list:
            key_list = set(substitution['keys'])
            if letter in key_list:
                found_keys += 1
                if found_keys == replacement_step:
                    cropped_word = word[current_position:]
                    return (substitution['value'] + cropped_word)

# Проверка фразы на неверные символы
def verify_phrase (phrase):
    pattern = re.compile(regexp_pattern)
    match = pattern.fullmatch(phrase)
    return match

# Создаём API-интерфейс
app = FastAPI(
    openapi_url = "/api/figalize/openapi.json",
    docs_url="/api/figalize/docs"
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
    app_name="figalize",
    prefix='figalize',
    labels={
        "server_name": os.getenv("HOSTNAME"),
    },
    group_paths=True,
    buckets=[0.025, 0.037, 0.05, 0.064, 0.079, 0.096, 0.115, 0.135, 0.157, 0.181, 0.208, 0.238, 0.27, 0.305, 0.344, 0.386, 0.432, 0.483, 0.539, 0.6, 0.667, 0.741, 0.822, 0.91, 1.007, 1.113, 1.23, 1.358, 1.498, 1.651, 1.82, 2.004, 2.207, 2.428, 2.672, 2.938],
    skip_paths=[
        '/api/healthz',
        '/metrics'],
    always_use_int_status=False
    )
app.add_route("/metrics", handle_metrics)

# Описываем обработку запроса к API фигализации
@app.post("/api/figalize/", status_code=200)
async def api_figalize_phrase(request: Request, response: Response):
    figalized_result = ''
    print('Incoming request:', request)
    if verify_phrase(request.phrase):
        for phrase_word in request.phrase.split(' '):
            figalized_result += (figalize (phrase_word,schemas[request.schema_id]['substitutions']) + ' ')
        else:
            history_data = (json.dumps(({'original':request.phrase, 'figalized':figalized_result}), indent = 4, ensure_ascii=False)).encode('utf-8').decode('unicode-escape')
            print (history_data)
            # При успешном завершении фигализации, отправляем запрос к API History, чтобы дополнить историю фигализаций
            try:
                requests.post(append_history_url, data = history_data)
            except Exception as err:
                print ('Ошибка при попытке обратиться к append_history_url, ', err)
            finally:
                return {'data': figalized_result}
    else:
        # Если фраза содержит неверные символы, возвращаем код 400 и сообщение об ошибке
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'data':'По-русски, пожалуйста, у нас тут культурное заведение'}

# Описываем обработку запроса списка схем
@app.get("/api/getschemas/", status_code=200)
async def api_getschemas():
    # Добавляем случайную задержку, чтобы график метрик смотрелся интереснее. 
    random_latency = random.uniform(0.001, 1)
    time.sleep(random_latency)
    count = 0
    schema_list = {}
    for schema in schemas:
        schema_list[count]=schema['name']
        count += 1
    return schema_list

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

# Подгружаем схемы фигализации из файла
schemas = load_schemas(json_path)

