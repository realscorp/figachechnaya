import re
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg
import os
import time
from starlette_exporter import PrometheusMiddleware, handle_metrics

regexp_pattern = "[а-яА-Яеё,. ]+"
# Глубина запроса к истории
history_count = 1
system_is_ready = False
# Забираем настройки из переменных окружения, всё по best practices
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']
db_name = os.environ['DB_NAME']
db_login = os.environ['DB_LOGIN']
db_pass = os.environ['DB_PASS']
# Собираем строку подключения для удобства
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
app = FastAPI(
    # Так как API работает через ревер-прокси ингресса, необходимо поменять пути для автодокументации
    openapi_url = "/api/history/openapi.json",
    docs_url="/api/history/docs"
)
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
# Создаём экспортер метрик
app.add_middleware(
    PrometheusMiddleware,
    app_name="history",
    prefix='history',
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

# Описываем обработку запроса к API добавления записи в историю
@app.post("/api/append/", status_code=200)
async def append_history(appendrequest: AppendRequest, response: Response):
    # Получаем доступ к переменной-флагу, объявленной глобально
    global system_is_ready
    # Отладочная информация в консоль
    print ('Incoming append request, original ' + appendrequest.original + ', figalized: ' + appendrequest.figalized)
    # Так как API будет доступно снаружи, делаем проверку на лишние символы для безопасности
    if not (verify_phrase(appendrequest.original) and verify_phrase(appendrequest.figalized)):
        print('Недопустимые символы')
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    # Делаем вставку в таблицу переданных значений
    try:
        async with await psycopg.AsyncConnection.connect(db_connection_string) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
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
async def get_history(response: Response):
    global system_is_ready
    # Пробуем выполнить запрос к БД
    try:
        async with await psycopg.AsyncConnection.connect(db_connection_string) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
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
async def metrics(response: Response):
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
