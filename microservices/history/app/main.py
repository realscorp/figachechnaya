import re
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg
import os
import time

regexp_pattern = "[а-яА-Яеё,. ]+"
history_count = 1
system_is_ready = False
db_host = 'localhost'
db_port = '5432'
db_name = 'history'
db_login = 'history'
# Секрет получаем из переменных окружения контейнера
db_pass = os.environ['DB_PASS']
db_connection_string = ('host=' + db_host + 
                        ' port=' + db_port +
                        ' dbname=' + db_name +
                        ' user=' + db_login +
                        ' password=' + db_pass
                        )

# Создаём свой тип данных, чтобы загружать в него данные из запроса
class AppendRequest(BaseModel):
    original: str
    figalized: str

def init_table():
    global system_is_ready
    print ('Initializing DB...')
    try:
        with psycopg.connect(db_connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''CREATE TABLE IF NOT EXISTS HISTORY(
                    ID SERIAL PRIMARY KEY,
                    ORIGINAL TEXT,
                    FIGALIZED TEXT
                    )''')
    except Exception:
        print ('Cannot initialize DB')
        system_is_ready = False
        return system_is_ready
    else:
        print ('DB initialized')
        system_is_ready = True
        return system_is_ready

# Проверка фразы на неверные символы
def verify_phrase (phrase):
    pattern = re.compile(regexp_pattern)
    match = pattern.fullmatch(phrase)
    return match

# Создаём API-интерфейс
app = FastAPI()
# Разрешаем обращение к API с любых доменов, так как внутри Kubernetes API будет недоступен снаружи
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

# Описываем обработку запроса к API добавления записи в историю
@app.post("/api/append/", status_code=200)
async def append_history(appendrequest: AppendRequest, response: Response):
    global system_is_ready
    print ('Incoming append request, original ' + appendrequest.original + ', figalized: ' + appendrequest.figalized)
    # Так как API будет доступно снаружи, делаем проверку на лишние символы для безопасности
    if not (verify_phrase(appendrequest.original) and verify_phrase(appendrequest.original)):
        print('Недопустимые символы')
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    # Делаем вставку в таблицу переданных значений
    try:
        with psycopg.connect(db_connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO history (original, figalized) VALUES (%s, %s)",
                    (appendrequest.original, appendrequest.figalized))
    # В случае сбоя выставляем флаг неготовности системы
    except:
        print ('Cannot append to history')
        system_is_ready = False
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return
    else:
        system_is_ready = True
        return
# API для запроса списка преобразованных слов из истории. У нас его использует фронтенд для генерации подсказки и отображения статистики
@app.get("/api/gethistory/", status_code=200)
def get_history(response: Response):
    global system_is_ready
    # Пробуем выполнить запрос к БД
    try:
        with psycopg.connect(db_connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM history ORDER BY id DESC LIMIT %s",
                    (history_count,))
                result_list = [list(x) for x in cur.fetchall()]
    # Если не получилось, выставляем флаг неготовности системы
    except:
        print ('Cannot get history')
        system_is_ready = False
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return
    else:
        system_is_ready = True
        return result_list

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

# На старте постоянно пытаемся выполнить инициализацию таблицы
# Пока не получится, флаг готовности системы будет false
while not init_table():
    time.sleep(1)
