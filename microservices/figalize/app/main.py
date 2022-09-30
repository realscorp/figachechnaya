import re
import json
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from prometheus_client import start_http_server, Summary, Counter, Gauge, Histogram
import os

system_is_ready = False
regexp_pattern = "[а-яА-Яеё,. ]+"
json_path = '/var/config/example.json'

# Забираем настройки из переменных окружения, всё по best practices
append_history_url = os.environ['HISTORY_APPEND_URL']
metrics_port = os.environ['METRICS_PORT_FIGALIZE']

# Инициализируем каунтеры для экспорта метрик
figalize_latency_seconds = Histogram('figalize_latency_seconds', 'Latency histogram for Figalize request processing')
figalize_count = Counter('figalize_count', 'Number of times Figalize requests was processed',['result'])
get_schemas_latency_seconds = Histogram('get_schemas_latency_seconds', 'Latency histogram for get Schemas request processing')
get_schemas_count = Counter('get_schemas_success_count', 'Number of times get Schemas requests was processed',['result'])

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
app = FastAPI()
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

# Описываем обработку запроса к API фигализации
@app.post("/api/figalize/", status_code=200)
async def api_figalize_phrase(request: Request, response: Response):
    with figalize_latency_seconds.time():
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
                # Обновляем метрику
                figalize_count.labels('success').inc()
                return {'data': figalized_result}
        else:
            # Если фраза содержит неверные символы, возвращаем код 400 и сообщение об ошибке
            figalize_count.labels('fail').inc()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'data':'По-русски, пожалуйста, у нас тут культурное заведение'}

# Описываем обработку запроса списка схем
@app.get("/api/getschemas/", status_code=200)
async def api_getschemas():
    with get_schemas_latency_seconds.time():
        count = 0
        schema_list = {}
        for schema in schemas:
            schema_list[count]=schema['name']
            count += 1
        get_schemas_count.labels('success').inc()
        return schema_list

# readinessProbe для Кубернетес
@app.get("/api/healthz/")
def get_history(response: Response):
    global system_is_ready
    if system_is_ready:
        response.status_code = status.HTTP_200_OK
        return
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return

# Подгружаем схемы фигализации из файла
schemas = load_schemas(json_path)
start_http_server(int(metrics_port))
