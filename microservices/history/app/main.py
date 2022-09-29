from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg

history_count = 1
db_host = 'localhost'
db_port = '5432'
db_name = 'history'
db_login = 'history'
db_pass = 'OneTwoTri4'
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
    with psycopg.connect(db_connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute(
                '''CREATE TABLE IF NOT EXISTS HISTORY(
                ID SERIAL PRIMARY KEY,
                ORIGINAL TEXT,
                FIGALIZED TEXT
                )''')


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
async def append_history(appendrequest: AppendRequest):
    print ('Incoming append request, original ' + appendrequest.original + ', figalized: ' + appendrequest.figalized)
    with psycopg.connect(db_connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO history (original, figalized) VALUES (%s, %s)",
                (appendrequest.original, appendrequest.figalized))

@app.get("/api/gethistory/", status_code=200)
def get_history():
    with psycopg.connect(db_connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM history ORDER BY id DESC LIMIT %s",
                (history_count,))
            result_list = [list(x) for x in cur.fetchall()]
            return result_list

# a : AppendRequest
# a.original = 'велосипед'
# a.figalized = 'фигасипед'
init_table()
# append_history (a)
# print(get_history(11))