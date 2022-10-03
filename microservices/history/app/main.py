import re
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg
import os
import time
from prometheus_client import start_http_server, Summary, Counter, Gauge, Histogram

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
metrics_port = os.environ['METRICS_PORT_HISTORY']
# Собираем строку подключения для удобства
db_connection_string = ('host=' + db_host + 
                        ' port=' + db_port +
                        ' dbname=' + db_name +
                        ' user=' + db_login +
                        ' password=' + db_pass
                        )

# Инициализируем каунтеры для экспорта метрик
history_appends_latency_seconds = Histogram('history_appends_latency_seconds', 'Latency histogram for History append request processing')
history_appends_count = Counter('history_appends_count', 'Number of times History append requests was processed',['result'])
history_get_latency_seconds = Histogram('history_get_latency_seconds', 'Latency histogram for get History request processing')
history_get_count = Counter('history_get_success_count', 'Number of times get History requests was processed',['result'])

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

# Описываем обработку запроса к API добавления записи в историю
@app.post("/api/append/", status_code=200)
async def append_history(appendrequest: AppendRequest, response: Response):
    with history_appends_latency_seconds.time():
        # Получаем доступ к переменной-флагу, объявленной глобально
        global system_is_ready
        # Отладочная информация в консоль
        print ('Incoming append request, original ' + appendrequest.original + ', figalized: ' + appendrequest.figalized)
        # Так как API будет доступно снаружи, делаем проверку на лишние символы для безопасности
        if not (verify_phrase(appendrequest.original) and verify_phrase(appendrequest.figalized)):
            print('Недопустимые символы')
            history_appends_count.labels('fail').inc()
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
            history_appends_count.labels('fail').inc()
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return
        else:
            history_appends_count.labels('success').inc()
            system_is_ready = True
            return

# API для запроса списка преобразованных слов из истории. У нас его использует фронтенд для генерации подсказки и отображения статистики
@app.get("/api/gethistory/", status_code=200)
def get_history(response: Response):
    with history_get_latency_seconds.time():
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
            history_get_count.labels('fail').inc()
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return
        else:
            history_get_count.labels('success').inc()
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
start_http_server(int(metrics_port))